@app.route("/", methods=["GET"])
def index():
	return render_template("index.html"), 200