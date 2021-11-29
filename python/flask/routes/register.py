from html import escape
from re import fullmatch
from Flask import session, render_template, redirect
from werkzeug.security import generate_password_hash

@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # html.escape() escapes potentially malicious characters
        username = html.escape(request.form.get("username"))
        email = html.escape(request.form.get("email").lower())
        password = html.escape(request.form.get("password"))
        confirmPassword = html.escape(request.form.get("confirm-password"))

        # RegExs to validate inputs
        userRegEx = '[A-Za-z0-9._-]{3,16}'
        emailRegEx = '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
        passRegEx = '[A-Za-z0-9¡!¿?$+._-]{6,16}'

        # Check if username is valid or not
        if not re.fullmatch(userRegEx, username):
            if len(username) < 3 or len(username) > 16:
                errorMessage = 'Username must be at least 3 characters, with a maximum of 16 characters.'
                return render_template("register.html", errorMessage=errorMessage)

            errorMessage = 'Invalid username. Please, use valid special characters (underscore, minus, and periods).'
            return render_template('register.html', errorMessage=errorMessage)

        elif len(email) < 6 or len(email) > 64:
            errorMessage = 'Email must be at least 6 characters, with a maximum of 64 characters.'
            return render_template("register.html", errorMessage=errorMessage)

        # Check if email is valid or not
        elif not re.fullmatch(emailRegEx, email):
            errorMessage = 'Invalid email. Please, try again.'
            return render_template("register.html", errorMessage=errorMessage)

        elif password != confirmPassword:
            errorMessage = 'Password and confirmation does not match. Please, try again.'
            return render_template("register.html", errorMessage=errorMessage)

        elif not re.fullmatch(passRegEx, password):
            if len(password) < 6 or len(password) > 16:
                errorMessage = 'Password must be at least 6 characters, with a maximum of 16 characters.'
                return render_template("register.html", errorMessage=errorMessage)

            errorMessage = 'Invalid password. Please, use valid special characters.'
            return render_template("register.html", errorMessage=errorMessage)

        # Check both if username or password have two or more consecutive periods
        elif '..' in username or '..' in password:
            errorMessage = 'Username and password cannot contain two or more consecutive periods (.).'
            return render_template("register.html", errorMessage=errorMessage)

        # Check both if username and/or password already exists. If not, then the account is created
        else:
            exists = db.execute("SELECT username FROM users WHERE username = ?", username)
            if exists:
                errorMessage = 'The username is already taken. Please, try again.'
                return render_template("register.html", errorMessage=errorMessage)

            exists = db.execute("SELECT email FROM users WHERE email = ?", email)
            if exists:
                errorMessage = 'The email is already in use. Please, try again, or '
                return render_template("register.html", errorMessage=errorMessage, emailExists=True)

            hashedPassword = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

            db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", username, email, hashedPassword)
            userId = db.execute("SELECT id FROM users WHERE username = ?", username)
            session["user_id"] = userId

            return redirect("/")

    return render_template("register.html")