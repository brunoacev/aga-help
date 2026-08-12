import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import makeWASocket, {
  DisconnectReason,
  downloadMediaMessage,
  fetchLatestBaileysVersion,
  isJidUser,
  isLidUser,
  useMultiFileAuthState,
} from "@whiskeysockets/baileys";
import pino from "pino";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const AUTH_DIR = path.join(__dirname, "auth_info");
const MEDIA_DIR = path.join(__dirname, "media_cache");
const PORT = Number(process.env.WHATSAPP_BRIDGE_PORT || 5001);
const MAX_MESSAGES_PER_CHAT = 300;

const app = express();
app.use(express.json());

let status = "DISCONNECTED";
let currentQr = "";
let connectedPhone = "";
let sock = null;
let starting = false;

const chatStore = new Map();
const messageStore = new Map();
const messageKeys = new Map();
const messageRawStore = new Map();
const groupMetadataCache = new Map();
const contactStore = new Map();
const lidPhoneMap = new Map();

function isGroupJid(jid) {
  return Boolean(jid && jid.endsWith("@g.us"));
}

function normalizePhoneJid(value) {
  if (!value) return "";
  const raw = String(value).trim();
  if (!raw) return "";
  if (raw.includes("@")) {
    return isJidUser(raw) || raw.endsWith("@s.whatsapp.net") ? raw.split(":")[0] + "@s.whatsapp.net" : "";
  }
  const digits = raw.replace(/\D/g, "");
  if (!digits) return "";
  return `${digits}@s.whatsapp.net`;
}

function registerLidPhone(lidJid, phoneJid) {
  const lid = String(lidJid || "").trim();
  const phone = normalizePhoneJid(phoneJid);
  if (lid && phone && isLidUser(lid)) {
    lidPhoneMap.set(lid, phone);
  }
}

function storeContact(contact) {
  if (!contact?.id) return;
  contactStore.set(contact.id, { ...(contactStore.get(contact.id) || {}), ...contact });
  if (contact.lid) {
    contactStore.set(contact.lid, { ...(contactStore.get(contact.lid) || {}), ...contact, id: contact.lid });
    if (contact.jid) registerLidPhone(contact.lid, contact.jid);
  }
  if (contact.jid) {
    const phoneJid = normalizePhoneJid(contact.jid);
    if (phoneJid) {
      contactStore.set(phoneJid, { ...(contactStore.get(phoneJid) || {}), ...contact, id: phoneJid });
      if (contact.lid) registerLidPhone(contact.lid, phoneJid);
    }
  }
  if (isLidUser(contact.id) && contact.jid) {
    registerLidPhone(contact.id, contact.jid);
  }
  if (isJidUser(contact.id) && contact.lid) {
    registerLidPhone(contact.lid, contact.id);
  }
}

function jidDigits(jid) {
  return String(jid || "").split("@")[0].split(":")[0].replace(/\D/g, "");
}

function isPhoneLike(value, jid) {
  const digits = String(value || "").replace(/\D/g, "");
  const phoneDigits = jidDigits(jid);
  if (!digits || digits.length < 10) return false;
  if (!phoneDigits) return digits.length >= 10;
  return digits === phoneDigits || digits.endsWith(phoneDigits.slice(-10));
}

function resolvePhoneJid(jid) {
  if (!jid) return "";
  if (isJidUser(jid) || jid.endsWith("@s.whatsapp.net")) {
    return normalizePhoneJid(jid);
  }
  if (isLidUser(jid)) {
    const mapped = lidPhoneMap.get(jid);
    if (mapped) return mapped;
    const contact = contactStore.get(jid);
    if (contact?.jid) return normalizePhoneJid(contact.jid);
  }
  return "";
}

function resolveContactName(jid) {
  if (isGroupJid(jid)) return "";
  const phoneJid = resolvePhoneJid(jid) || jid;
  const candidates = [];
  for (const key of [jid, phoneJid]) {
    const contact = contactStore.get(key);
    if (contact) {
      candidates.push(contact.name, contact.notify, contact.verifiedName);
    }
  }
  const chat = chatStore.get(jid);
  if (chat) {
    candidates.push(chat.name, chat.verifiedName);
  }
  for (const candidate of candidates) {
    const value = String(candidate || "").trim();
    if (value && !value.includes("@") && !isPhoneLike(value, phoneJid)) {
      return value;
    }
  }
  return "";
}

function formatPhoneFromJid(jid) {
  const phoneJid = resolvePhoneJid(jid);
  if (!phoneJid) return "";
  const raw = phoneJid.split("@")[0].split(":")[0];
  return raw.startsWith("+") ? raw : `+${raw}`;
}

function formatPhone(jid) {
  return formatPhoneFromJid(jid) || "";
}

function jidFromTarget(target) {
  if (!target) return "";
  if (target.includes("@")) return target;
  const digits = String(target).replace(/\D/g, "");
  return `${digits}@s.whatsapp.net`;
}

function rawMessageKey(chatId, msgId) {
  return `${chatId}:${msgId}`;
}

function storeRawMessage(msg) {
  const chatId = msg.key?.remoteJid;
  const msgId = msg.key?.id;
  if (chatId && msgId) {
    messageRawStore.set(rawMessageKey(chatId, msgId), msg);
  }
}

function messageKind(msg) {
  const content = msg.message || {};
  if (content.audioMessage) return "audio";
  if (content.imageMessage) return "image";
  if (content.videoMessage) return "video";
  if (content.documentMessage) return "document";
  if (content.stickerMessage) return "sticker";
  return "text";
}
function extractMessageText(msg) {
  const content = msg.message || {};
  if (content.conversation) return content.conversation;
  if (content.extendedTextMessage?.text) return content.extendedTextMessage.text;
  if (content.imageMessage) return content.imageMessage.caption || "📷 Foto";
  if (content.videoMessage) return content.videoMessage.caption || "🎬 Vídeo";
  if (content.audioMessage) return content.audioMessage.ptt ? "🎤 Áudio" : "🔊 Áudio";
  if (content.documentMessage) {
    return `📄 ${content.documentMessage.fileName || "Documento"}`;
  }
  if (content.stickerMessage) return "🎨 Figurinha";
  if (content.contactMessage) return "👤 Contato";
  if (content.locationMessage) return "📍 Localização";
  if (content.reactionMessage) return content.reactionMessage.text || "Reação";
  return "";
}

function parseMessage(msg) {
  const text = extractMessageText(msg);
  const kind = messageKind(msg);
  const tsRaw = msg.messageTimestamp ? Number(msg.messageTimestamp) : Date.now() / 1000;
  const ts = new Date(tsRaw * (tsRaw > 1e12 ? 1 : 1000));
  const participant = msg.key?.participant || "";
  if (participant && msg.key?.senderPn) {
    registerLidPhone(participant, msg.key.senderPn);
  }
  const senderPhoneJid = participant ? resolvePhoneJid(participant) || normalizePhoneJid(msg.key?.senderPn) : "";
  return {
    id: msg.key?.id || "",
    from_me: Boolean(msg.key?.fromMe),
    text,
    time: ts.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
    timestamp: ts.getTime(),
    type: kind,
    has_media: kind === "audio",
    sender_jid: participant,
    sender_name: resolveContactName(participant) || msg.pushName || "",
    sender_phone: senderPhoneJid ? formatPhoneFromJid(senderPhoneJid) : "",
  };
}

async function getGroupMeta(jid) {
  if (!isGroupJid(jid)) return null;
  if (groupMetadataCache.has(jid)) {
    return groupMetadataCache.get(jid);
  }
  if (!sock) {
    return { subject: "Grupo", avatar: "" };
  }
  try {
    const meta = await sock.groupMetadata(jid);
    let avatar = "";
    try {
      avatar = await sock.profilePictureUrl(jid, "image");
    } catch (_) {
      /* avatar opcional */
    }
    const entry = {
      subject: meta.subject || "Grupo",
      avatar,
    };
    groupMetadataCache.set(jid, entry);
    return entry;
  } catch (_) {
    const fallback = { subject: "Grupo", avatar: "" };
    groupMetadataCache.set(jid, fallback);
    return fallback;
  }
}

function sortMessages(messages) {
  return [...messages].sort((a, b) => a.timestamp - b.timestamp);
}

function appendMessage(msg) {
  const jid = msg.key?.remoteJid;
  if (!jid || jid.includes("@broadcast")) return null;

  if (isLidUser(jid) && msg.key?.senderPn && !msg.key?.fromMe) {
    registerLidPhone(jid, msg.key.senderPn);
  }

  const parsed = parseMessage(msg);
  if (!parsed.text && parsed.type !== "audio") return null;

  storeRawMessage(msg);

  const bucket = messageStore.get(jid) || [];
  if (parsed.id && bucket.some((item) => item.id === parsed.id)) {
    return null;
  }

  bucket.push(parsed);
  messageStore.set(jid, sortMessages(bucket).slice(-MAX_MESSAGES_PER_CHAT));

  if (parsed.id) {
    const keys = messageKeys.get(jid) || [];
    keys.push({ remoteJid: jid, id: parsed.id, fromMe: parsed.from_me });
    messageKeys.set(jid, keys.slice(-MAX_MESSAGES_PER_CHAT));
  }

  const chat = chatStore.get(jid) || { id: jid };
  chatStore.set(jid, {
    ...chat,
    conversation: parsed.text,
    conversationTimestamp: parsed.timestamp,
  });

  if (!isGroupJid(jid) && msg.pushName && !msg.key?.fromMe) {
    const prev = contactStore.get(jid) || { id: jid };
    if (!prev.name && !prev.notify) {
      storeContact({ ...prev, id: jid, name: msg.pushName, notify: msg.pushName });
    }
    const phoneJid = resolvePhoneJid(jid);
    if (phoneJid) {
      const phoneContact = contactStore.get(phoneJid) || { id: phoneJid, jid: phoneJid };
      if (!phoneContact.name && !phoneContact.notify) {
        storeContact({ ...phoneContact, name: msg.pushName, notify: msg.pushName });
      }
    }
  }

  return parsed;
}

async function formatChat(chat) {
  const last =
    chat.conversation ||
    chat.lastMessage?.conversation ||
    chat.lastMessage?.extendedTextMessage?.text ||
    "";
  const isGroup = isGroupJid(chat.id);
  let name = chat.name || "";
  let groupName = "";
  let avatar = "";

  if (isGroup) {
    const meta = await getGroupMeta(chat.id);
    groupName = meta?.subject || chat.subject || chat.name || "Grupo";
    name = groupName;
    avatar = meta?.avatar || "";
  } else {
    name = resolveContactName(chat.id);
  }

  return {
    id: chat.id,
    name,
    contact_name: isGroup ? "" : name,
    phone: isGroup ? "" : formatPhoneFromJid(chat.id),
    last_message: last,
    unread: chat.unreadCount || 0,
    timestamp: chat.conversationTimestamp || 0,
    is_group: isGroup,
    group_name: isGroup ? groupName : "",
    avatar,
  };
}

function bindEvents(socket) {
  socket.ev.on("messaging-history.set", ({ chats, messages, contacts }) => {
    for (const chat of chats || []) chatStore.set(chat.id, chat);
    for (const contact of contacts || []) storeContact(contact);
    for (const msg of messages || []) appendMessage(msg);
  });

  socket.ev.on("chats.set", ({ chats }) => {
    for (const chat of chats) chatStore.set(chat.id, chat);
  });

  socket.ev.on("chats.upsert", (chats) => {
    for (const chat of chats) chatStore.set(chat.id, chat);
  });

  socket.ev.on("chats.update", (updates) => {
    for (const update of updates) {
      const prev = chatStore.get(update.id) || { id: update.id };
      chatStore.set(update.id, { ...prev, ...update });
    }
  });

  socket.ev.on("contacts.upsert", (contacts) => {
    for (const contact of contacts || []) storeContact(contact);
  });

  socket.ev.on("contacts.update", (updates) => {
    for (const update of updates || []) {
      if (!update?.id) continue;
      storeContact({ ...(contactStore.get(update.id) || { id: update.id }), ...update });
    }
  });

  socket.ev.on("chats.phoneNumberShare", ({ lid, jid }) => {
    registerLidPhone(lid, jid);
  });

  socket.ev.on("messages.upsert", ({ messages, type }) => {
    for (const msg of messages || []) {
      appendMessage(msg);
    }
  });

  socket.ev.on("groups.update", (updates) => {
    for (const update of updates || []) {
      const jid = update.id;
      if (!isGroupJid(jid)) continue;
      const prev = groupMetadataCache.get(jid) || { subject: "Grupo", avatar: "" };
      groupMetadataCache.set(jid, {
        ...prev,
        subject: update.subject || prev.subject,
      });
    }
  });
}

async function connectWhatsApp() {
  if (starting) return;
  starting = true;
  status = "DISCONNECTED";
  currentQr = "";

  if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
  }

  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: "silent" }),
    printQRInTerminal: false,
    syncFullHistory: false,
  });

  sock.ev.on("creds.update", saveCreds);
  bindEvents(sock);

  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      currentQr = qr;
      status = "QR_READY";
    }

    if (connection === "open") {
      status = "CONNECTED";
      currentQr = "";
      connectedPhone = formatPhone(sock.user?.id);
      starting = false;
    }

    if (connection === "close") {
      const code = lastDisconnect?.error?.output?.statusCode;
      const loggedOut = code === DisconnectReason.loggedOut;
      status = "DISCONNECTED";
      currentQr = "";
      connectedPhone = "";
      sock = null;
      starting = false;
      chatStore.clear();
      messageStore.clear();
      messageKeys.clear();
      messageRawStore.clear();
      groupMetadataCache.clear();
      contactStore.clear();
      lidPhoneMap.clear();
      if (!loggedOut) {
        setTimeout(connectWhatsApp, 2500);
      }
    }
  });

  starting = false;
}

app.get("/health", (_req, res) => {
  res.json({ ok: true, status });
});

app.get("/status", (_req, res) => {
  res.json({
    status,
    phone: connectedPhone,
  });
});

app.get("/qr", (_req, res) => {
  if (status !== "QR_READY" || !currentQr) {
    return res.json({ qr: "" });
  }
  res.json({ qr: currentQr });
});

app.get("/chats", async (_req, res) => {
  if (status !== "CONNECTED") {
    return res.json({ chats: [] });
  }
  try {
    const rows = Array.from(chatStore.values())
      .filter((chat) => chat.id && !chat.id.includes("@broadcast"))
      .sort((a, b) => (b.conversationTimestamp || 0) - (a.conversationTimestamp || 0))
      .slice(0, 100);
    const chats = await Promise.all(rows.map((chat) => formatChat(chat)));
    res.json({ chats });
  } catch (error) {
    res.status(500).json({ chats: [], error: String(error.message || error) });
  }
});

app.get("/messages", (req, res) => {
  const chatId = req.query.chat_id;
  if (!chatId || status !== "CONNECTED") {
    return res.json({ messages: [] });
  }
  const messages = sortMessages(messageStore.get(chatId) || []);
  res.json({ messages });
});

app.get("/media", async (req, res) => {
  const chatId = req.query.chat_id;
  const msgId = req.query.msg_id;
  if (!chatId || !msgId) {
    return res.status(400).json({ ok: false, error: "chat_id e msg_id são obrigatórios" });
  }
  if (!sock || status !== "CONNECTED") {
    return res.status(503).json({ ok: false, error: "WhatsApp desconectado" });
  }

  const cachePath = path.join(MEDIA_DIR, `${Buffer.from(`${chatId}:${msgId}`).toString("hex")}.ogg`);
  try {
    if (fs.existsSync(cachePath)) {
      res.setHeader("Content-Type", "audio/ogg");
      return res.sendFile(cachePath);
    }

    const raw = messageRawStore.get(rawMessageKey(chatId, msgId));
    if (!raw) {
      return res.status(404).json({ ok: false, error: "Mídia não encontrada para esta mensagem" });
    }

    const logger = pino({ level: "silent" });
    const buffer = await downloadMediaMessage(
      raw,
      "buffer",
      {},
      { logger, reuploadRequest: sock.updateMediaMessage },
    );

    if (!fs.existsSync(MEDIA_DIR)) {
      fs.mkdirSync(MEDIA_DIR, { recursive: true });
    }
    fs.writeFileSync(cachePath, buffer);

    const mimetype = raw.message?.audioMessage?.mimetype || "audio/ogg";
    res.setHeader("Content-Type", String(mimetype).split(";")[0] || "audio/ogg");
    res.send(buffer);
  } catch (error) {
    res.status(500).json({ ok: false, error: String(error.message || error) });
  }
});

app.post("/send", async (req, res) => {
  try {
    const { to, message, chat_id: chatId } = req.body || {};
    const text = String(message || "").trim();
    if (!text) {
      return res.status(400).json({ ok: false, error: "Mensagem vazia" });
    }
    if (!sock || status !== "CONNECTED") {
      return res.status(503).json({ ok: false, error: "WhatsApp desconectado" });
    }
    const jid = jidFromTarget(chatId || to);
    const sent = await sock.sendMessage(jid, { text });
    appendMessage({
      key: { remoteJid: jid, fromMe: true, id: sent?.key?.id || `local-${Date.now()}` },
      message: { conversation: text },
      messageTimestamp: Math.floor(Date.now() / 1000),
    });
    res.json({ ok: true, chat_id: jid });
  } catch (error) {
    res.status(500).json({ ok: false, error: String(error.message || error) });
  }
});

app.post("/read", async (req, res) => {
  try {
    const chatId = req.body?.chat_id;
    if (!chatId || !sock || status !== "CONNECTED") {
      return res.status(400).json({ ok: false, error: "Chat inválido ou desconectado" });
    }
    const keys = (messageKeys.get(chatId) || []).filter((item) => !item.fromMe).slice(-5);
    if (keys.length) {
      await sock.readMessages(keys);
    }
    const chat = chatStore.get(chatId);
    if (chat) {
      chatStore.set(chatId, { ...chat, unreadCount: 0 });
    }
    res.json({ ok: true });
  } catch (error) {
    res.status(500).json({ ok: false, error: String(error.message || error) });
  }
});

app.post("/logout", async (_req, res) => {
  try {
    if (sock) {
      try {
        await sock.logout();
      } catch (_) {
        sock.end(undefined);
      }
    }
    sock = null;
    status = "DISCONNECTED";
    currentQr = "";
    connectedPhone = "";
    chatStore.clear();
    messageStore.clear();
    messageKeys.clear();
    messageRawStore.clear();
    groupMetadataCache.clear();
    contactStore.clear();
    lidPhoneMap.clear();
    if (fs.existsSync(AUTH_DIR)) {
      fs.rmSync(AUTH_DIR, { recursive: true, force: true });
    }
    setTimeout(connectWhatsApp, 800);
    res.json({ ok: true });
  } catch (error) {
    res.status(500).json({ ok: false, error: String(error.message || error) });
  }
});

app.post("/restart", async (_req, res) => {
  currentQr = "";
  status = "DISCONNECTED";
  if (sock) {
    try {
      sock.end(undefined);
    } catch (_) {
      /* ignore */
    }
    sock = null;
  }
  await connectWhatsApp();
  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log(`AGA HELP WhatsApp bridge em http://localhost:${PORT}`);
  connectWhatsApp().catch((error) => {
    console.error("Falha ao iniciar WhatsApp:", error);
    status = "DISCONNECTED";
  });
});
