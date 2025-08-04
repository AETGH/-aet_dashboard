# === app.py ===
from flask import Flask, render_template
from api import api_blueprint
from models import init_db, get_all_clients

app = Flask(__name__)
app.register_blueprint(api_blueprint)

@app.route("/")
def dashboard():
    clients = get_all_clients()
    return render_template("dashboard.html", clients=clients)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8081, debug=True)


# === api.py ===
from flask import Blueprint, request, jsonify
from models import upsert_client, add_command, get_pending_commands
import datetime

api_blueprint = Blueprint("api", __name__, url_prefix="/api")

@api_blueprint.route("/status", methods=["POST"])
def status():
    data = request.get_json()
    data["last_seen"] = datetime.datetime.utcnow().isoformat()
    upsert_client(data)
    return jsonify({"message": "Status gespeichert"})

@api_blueprint.route("/commands", methods=["GET"])
def commands():
    client_id = request.args.get("client_id")
    cmds = get_pending_commands(client_id)
    return jsonify({"commands": cmds})

@api_blueprint.route("/command", methods=["POST"])
def command():
    data = request.get_json()
    client_id = data.get("client_id")
    cmd = data.get("cmd")
    args = data.get("args", None)
    add_command(client_id, cmd, args)
    return jsonify({"message": "Command added"})


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


# === templates/dashboard.html ===
<!DOCTYPE html>
<html>
<head>
  <title>aet-dashboard</title>
  <style>
    body { font-family: sans-serif; background: #111; color: #eee; padding: 2em; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid #444; padding: 8px; text-align: left; }
    th { background-color: #222; }
    tr:hover { background-color: #333; }
  </style>
</head>
<body>
  <h1>-@_Dashboard</h1>
  <table>
    <tr>
      <th>Client ID</th>
      <th>Hostname</th>
      <th>IP</th>
      <th>Uptime</th>
      <th>Modules</th>
      <th>Last Seen</th>
    </tr>
    {% for c in clients %}
    <tr>
      <td>{{ c.client_id }}</td>
      <td>{{ c.hostname }}</td>
      <td>{{ c.ip }}</td>
      <td>{{ c.uptime }}</td>
      <td><pre>{{ c.modules }}</pre></td>
      <td>{{ c.last_seen }}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
