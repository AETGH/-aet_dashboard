# === models.py ===
import sqlite3, json, os

DB_FILE = os.getenv("DB_PATH", "config/database.db")

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                hostname TEXT,
                ip TEXT,
                uptime TEXT,
                modules TEXT,
                info TEXT,
                last_seen TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,
                cmd TEXT,
                args TEXT,
                executed INTEGER DEFAULT 0,
                timestamp TEXT
            )
        """)
        conn.commit()

def upsert_client(data):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO clients (client_id, hostname, ip, uptime, modules, info, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(client_id) DO UPDATE SET
                hostname=excluded.hostname,
                ip=excluded.ip,
                uptime=excluded.uptime,
                modules=excluded.modules,
                info=excluded.info,
                last_seen=excluded.last_seen
        """, (
            data.get("client_id"),
            data.get("hostname"),
            data.get("ip"),
            data.get("uptime"),
            json.dumps(data.get("modules")),
            json.dumps(data.get("info")),
            data.get("last_seen")
        ))
        conn.commit()

def get_all_clients():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT * FROM clients ORDER BY last_seen DESC").fetchall()

def get_pending_commands(client_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cmds = conn.execute("""
            SELECT id, cmd, args FROM commands
            WHERE client_id=? AND executed=0
        """, (client_id,)).fetchall()
        return [dict(row) for row in cmds]

def add_command(client_id, cmd, args=None):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO commands (client_id, cmd, args, timestamp)
            VALUES (?, ?, ?, datetime('now'))
        """, (client_id, cmd, args))
        conn.commit()
