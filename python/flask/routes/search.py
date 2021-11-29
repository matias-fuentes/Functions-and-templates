from helpers import getUser, searchPost, query
from Flask import render_template, request

@app.route("/search", methods=["GET", "POST"])
def search():
    username = getUser(db)['username']
    if request.method == "POST":
        return searchPost()

    q = request.args.get('q')
    response = query(q, url)
    return render_template("search.html")