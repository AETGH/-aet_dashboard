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
