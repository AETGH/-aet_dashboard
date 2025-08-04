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
