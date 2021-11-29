from helpers import userOrEmail
from Flask import session, request, redirect, render_template
from re import fullmatch

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        search = request.form.get("search")
        if search:
            return redirect(f"/search?q={search}")

        user = request.form.get("user")
        password = request.form.get("password")

        # We can log in either with our username or with our email.
        # If there's an '@' in user, that means that we're dealing with an email.
        if '@' in user:
            user = user.lower()

            if len(user) < 6 or len(user) > 64:
                return render_template("login.html", error=True)

            elif not fullmatch(emailRegEx, user):
                return render_template("login.html", error=True)

            return userOrEmail(True, user, password, passRegEx, session, db)

        elif not fullmatch(userRegEx, user):
            return render_template("login.html", error=True)

        return userOrEmail(False, user, password, passRegEx, session, db)

    return render_template("login.html")
