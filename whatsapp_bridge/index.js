import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import makeWASocket, {
  DisconnectReason,
  fetchLatestBaileysVersion,
  useMultiFileAuthState,
} from "@whiskeysockets/baileys";
import pino from "pino";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const AUTH_DIR = path.join(__dirname, "auth_info");
const PORT = Number(process.env.WHATSAPP_BRIDGE_PORT || 5001);

const app = express();
app.use(express.json());

let status = "DISCONNECTED";
let currentQr = "";
let connectedPhone = "";
let sock = null;
let starting = false;

const chatStore = new Map();
const messageStore = new Map();

function formatPhone(jid) {
  if (!jid) return "";
  const raw = jid.split("@")[0].split(":")[0];
  return raw.startsWith("+") ? raw : `+${raw}`;
}

function jidFromTarget(target) {
  if (!target) return "";
  if (target.includes("@")) return target;
  const digits = String(target).replace(/\D/g, "");
  return `${digits}@s.whatsapp.net`;
}

function parseMessage(msg) {
  const text =
    msg.message?.conversation ||
    msg.message?.extendedTextMessage?.text ||
    msg.message?.imageMessage?.caption ||
    "";
  const ts = msg.messageTimestamp
    ? new Date(Number(msg.messageTimestamp) * 1000)
    : new Date();
  return {
    from_me: Boolean(msg.key.fromMe),
    text,
    time: ts.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
    timestamp: ts.getTime(),
  };
}

function formatChat(chat) {
  const last =
    chat.conversation ||
    chat.lastMessage?.conversation ||
    chat.lastMessage?.extendedTextMessage?.text ||
    "";
  return {
    id: chat.id,
    name: chat.name || formatPhone(chat.id),
    phone: formatPhone(chat.id),
    last_message: last,
    unread: chat.unreadCount || 0,
  };
}

function bindEvents(socket) {
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

  socket.ev.on("messages.upsert", ({ messages }) => {
    for (const msg of messages) {
      const jid = msg.key.remoteJid;
      if (!jid || jid.includes("@broadcast")) continue;
      const parsed = parseMessage(msg);
      const bucket = messageStore.get(jid) || [];
      bucket.push(parsed);
      messageStore.set(jid, bucket.slice(-200));
      const chat = chatStore.get(jid) || { id: jid };
      chatStore.set(jid, { ...chat, conversation: parsed.text, conversationTimestamp: parsed.timestamp });
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

app.get("/chats", (_req, res) => {
  if (status !== "CONNECTED") {
    return res.json({ chats: [] });
  }
  const chats = Array.from(chatStore.values())
    .filter((chat) => chat.id && !chat.id.includes("@broadcast"))
    .sort((a, b) => (b.conversationTimestamp || 0) - (a.conversationTimestamp || 0))
    .slice(0, 80)
    .map(formatChat);
  res.json({ chats });
});

app.get("/messages", (req, res) => {
  const chatId = req.query.chat_id;
  if (!chatId || status !== "CONNECTED") {
    return res.json({ messages: [] });
  }
  const messages = (messageStore.get(chatId) || []).sort((a, b) => a.timestamp - b.timestamp);
  res.json({ messages });
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
    await sock.sendMessage(jid, { text });
    const now = new Date();
    const parsed = {
      from_me: true,
      text,
      time: now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
      timestamp: now.getTime(),
    };
    const bucket = messageStore.get(jid) || [];
    bucket.push(parsed);
    messageStore.set(jid, bucket.slice(-200));
    res.json({ ok: true, chat_id: jid });
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
