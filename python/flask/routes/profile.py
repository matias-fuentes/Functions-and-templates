from helpers import getUser, uploadImage
from Flask import request, redirect, render_template

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = getUser(db)['username']
    if request.method == "POST":
        search = request.form.get("search")
        if search:
            return redirect(f"/search?q={search}")

        profilePic = request.files['profilePic']
        return uploadImage(db, profilePic, username)

    # Make another separately query to get the saved articles information
    picDirectory = db.execute("SELECT profilePicDir FROM users WHERE id = ?", session.get("user_id"))

    return render_template("profile.html", picDirectory=picDirectory, username=username, logIn=session.get("user_id"))