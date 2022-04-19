@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any userId
    session.clear()

    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")

        errorMessage = 'The email or password are incorrect. Please, try again.'
        # We can log in either with our username or with our email.
        # If there's an '@' in user, that means that we're dealing with an email.
        if '@' in user:
            user = user.lower() 

            if (len(user) < 6 or len(user) > 64) or not fullmatch(emailRegEx, user):
                return render_template("login.html", errorMessage=errorMessage), 401

            try:
                connection = pool.get_connection()
                cursor = connection.cursor()
            except:
                errorMessage = 'An error has occurred while establishing a connection with the database. Please, try again.'
                return render_template("login.html", errorMessage=errorMessage), 500

            validUser, message = validateUser(True, user, password, passRegEx, session, cursor, connection)
            if (validUser):
                redirect("/")
            else:
                return render_template("login.html", errorMessage=message), 401

        elif not fullmatch(userRegEx, user):
            return render_template("login.html", errorMessage=errorMessage), 401

        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
        except:
            errorMessage = 'An error has occurred while establishing a connection with the database. Please, try again.'
            return render_template("login.html", errorMessage=errorMessage), 500

        validUser, message = validateUser(True, user, password, passRegEx, session, cursor, connection)
        if (validUser):
            redirect("/")
        else:
            return render_template("login.html", errorMessage=message), 401

    return render_template("login.html"), 200