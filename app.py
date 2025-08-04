@app.route("/")
def dashboard():
    clients = get_all_clients()
    return render_template("dashboard.html", clients=clients)
