from datetime import datetime
from pathlib import Path
import random
import re
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "aga_help.db"
AGATEK_ADDRESS = "Agatek Persianas e Cortinas de Fortaleza"

def generate_random_address() -> str:
    return AGATEK_ADDRESS

def generate_random_profile(reseller_name: str) -> tuple[str, str]:
    ddd = "85"
    num1 = random.randint(98000, 99999)
    num2 = random.randint(1000, 9999)
    phone = f"({ddd}) {num1}-{num2}"
    return phone, AGATEK_ADDRESS

def init_db():
    """Inicializa as tabelas de pedidos, contatos e logs no banco de dados SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                reseller_name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                address TEXT DEFAULT '',
                value REAL NOT NULL,
                entry_date TEXT NOT NULL,
                deadline_date TEXT NOT NULL,
                description TEXT NOT NULL,
                width TEXT DEFAULT '',
                height TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Orçamento',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                address TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        for col in ["phone", "address", "width", "height"]:
            try:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
        conn.commit()

def add_log(action_type: str, description: str):
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO logs (action_type, description, created_at) VALUES (?, ?, ?)",
            (action_type, description, now_str)
        )
        conn.commit()

def get_logs():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 50").fetchall()]

def parse_vcf_content(vcf_text: str) -> list[tuple[str, str]]:
    contacts = []
    seen_phones = set()
    cards = re.split(r"END:VCARD", vcf_text, flags=re.IGNORECASE)
    
    for card in cards:
        if not card.strip():
            continue
            
        name = ""
        phone = ""
        
        fn_match = re.search(r"^FN(?:;[^:]*)?:(.*)$", card, re.MULTILINE | re.IGNORECASE)
        if fn_match:
            name = fn_match.group(1).strip()
        else:
            n_match = re.search(r"^N(?:;[^:]*)?:(.*)$", card, re.MULTILINE | re.IGNORECASE)
            if n_match:
                parts = n_match.group(1).split(";")
                cleaned_parts = [p.strip() for p in parts if p.strip()]
                if len(cleaned_parts) >= 2:
                    name = f"{cleaned_parts[1]} {cleaned_parts[0]}"
                elif len(cleaned_parts) == 1:
                    name = cleaned_parts[0]

        tel_matches = re.findall(r"^TEL(?:;[^:]*)?:(.*)$", card, re.MULTILINE | re.IGNORECASE)
        for raw_tel in tel_matches:
            digits = "".join(filter(str.isdigit, raw_tel))
            if digits.startswith("55") and len(digits) in (12, 13):
                digits = digits[2:]
                
            if len(digits) in (10, 11):
                if len(digits) == 11:
                    phone = f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
                else:
                    phone = f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
                break
            elif len(digits) >= 8:
                phone = raw_tel.strip()
                break

        if name and phone:
            clean_name = re.sub(r'[\r\n"]', '', name).strip()
            digits_key = "".join(filter(str.isdigit, phone))
            if digits_key and digits_key not in seen_phones:
                seen_phones.add(digits_key)
                contacts.append((clean_name, phone))
            
    return contacts

def import_vcf_contacts(vcf_text: str) -> int:
    contacts = parse_vcf_content(vcf_text)
    if not contacts:
        return 0

    count = 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with sqlite3.connect(DB_PATH) as conn:
        for name, phone in contacts:
            digits_phone = "".join(filter(str.isdigit, phone))
            
            exists = conn.execute("""
                SELECT 1 FROM contacts 
                WHERE name = ? OR (phone != '' AND REPLACE(REPLACE(REPLACE(REPLACE(phone, '(', ''), ')', ''), '-', ''), ' ', '') = ?)
                LIMIT 1
            """, (name, digits_phone)).fetchone()
            
            if not exists:
                conn.execute("""
                    INSERT INTO contacts (name, phone, address, created_at)
                    VALUES (?, ?, ?, ?)
                """, (name, phone, AGATEK_ADDRESS, now_str))
                count += 1
        conn.commit()

    if count > 0:
        add_log("IMPORTAÇÃO", f"Importados {count} novos contatos da agenda (.VCF).")
    return count

def clear_all_orders():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM orders")
        conn.commit()
    add_log("EXCLUSÃO", "Todos os pedidos do quadro Kanban foram limpos.")

def clear_all_contacts():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM contacts")
        conn.commit()
    add_log("EXCLUSÃO", "Todos os contatos da agenda foram removidos.")

def search_reseller_profiles(query: str, limit: int = 3):
    clean_q = query.strip()
    if not clean_q or len(clean_q) < 2:
        return []
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        sql = """
            SELECT name AS reseller_name, phone, address FROM contacts WHERE name LIKE ?
            UNION
            SELECT reseller_name, phone, address FROM orders WHERE reseller_name LIKE ? AND reseller_name != ''
            LIMIT ?
        """
        rows = conn.execute(sql, (f"%{clean_q}%", f"%{clean_q}%", limit)).fetchall()
        return [dict(r) for r in rows]

def get_profile_by_exact_name(reseller_name: str):
    clean_q = reseller_name.strip()
    if not clean_q:
        return None
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT phone, address FROM contacts WHERE name LIKE ? LIMIT 1", (clean_q,)).fetchone()
        if not row:
            row = conn.execute("SELECT phone, address FROM orders WHERE reseller_name LIKE ? ORDER BY id DESC LIMIT 1", (clean_q,)).fetchone()
        return dict(row) if row else None

def add_order(order_number: str, reseller_name: str, phone: str, address: str, value: float, entry_date: str, deadline_date: str, description: str, width: str = "", height: str = "", status: str = "Orçamento"):
    target_address = address if address.strip() else AGATEK_ADDRESS
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO orders (order_number, reseller_name, phone, address, value, entry_date, deadline_date, description, width, height, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_number, reseller_name, phone, target_address, value, entry_date, deadline_date, description, width, height, status, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
    add_log("NOVO PEDIDO", f"Pedido #{order_number} criado para {reseller_name}.")

def get_orders():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()]

def update_order_status(order_id: int, new_status: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()

def delete_order(order_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
    return True