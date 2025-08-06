# === api.py ===
from flask import Blueprint, request, jsonify
from models import upsert_client, add_command, get_pending_commands
import datetime

api_blueprint = Blueprint("api", __name__, url_prefix="/api")

@api_blueprint.route("/status", methods=["POST"])
def status():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
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
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    client_id = data.get("client_id")
    cmd = data.get("cmd")
    args = data.get("args", None)

    if not client_id or not cmd:
        return jsonify({"error": "client_id und cmd sind erforderlich"}), 400

        # HTMX: Live-Feedback
    if request.headers.get("HX-Request"):
        return f'<div id="feedback-{client_id}">✅ Befehl gesendet: <code>{cmd}</code></div>'

    return jsonify({"message": f"Command '{cmd}' für {client_id} gesetzt."})
    
    add_command(client_id, cmd, args)
    return jsonify({"message": f"Command '{cmd}' für {client_id} gesetzt."})
