@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any userId
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirmPassword = request.form.get("confirm-password")

        # Check if username is valid or not
        if not fullmatch(userRegEx, username):
            if len(username) < 3 or len(username) > 16:
                errorMessage = 'Username must be at least 3 characters, with a maximum of 16 characters.'
                return render_template("register.html", errorMessage=errorMessage), 422

            errorMessage = 'Invalid username. Please, use valid special characters (underscore, minus, and periods).'
            return render_template('register.html', errorMessage=errorMessage), 422

        # Check if email is valid or not
        elif not fullmatch(emailRegEx, email):
            if len(email) < 6 or len(email) > 64:
                errorMessage = 'Email must be at least 6 characters, with a maximum of 64 characters.'
                return render_template("register.html", errorMessage=errorMessage), 422

            errorMessage = 'Invalid email. Please, try again.'
            return render_template("register.html", errorMessage=errorMessage), 422

        # Check if password is equal to the confirmed password
        elif password != confirmPassword:
            errorMessage = 'Password and confirm does not match. Please, try again.'
            return render_template("register.html", errorMessage=errorMessage), 422

        # Check if password is valid or not
        elif not fullmatch(passRegEx, password):
            if len(password) < 6 or len(password) > 16:
                errorMessage = 'Password must be at least 6 characters, with a maximum of 16 characters.'
                return render_template("register.html", errorMessage=errorMessage), 422

            errorMessage = 'Invalid password. Please, use valid special characters.'
            return render_template("register.html", errorMessage=errorMessage), 422

        # Check both if username or password have two or more consecutive periods
        elif '..' in username or '..' in password:
            errorMessage = 'Username and password cannot contain two or more consecutive periods (.).'
            return render_template("register.html", errorMessage=errorMessage), 422

        # Check both if username and/or password already exists. If not, then the account is created
        else:
            try:
                connection = pool.get_connection()
                cursor = connection.cursor()

                exists = cursor.execute(f"SELECT username FROM users WHERE username = '{username}'")
                exists = cursor.fetchone()
            except:
                errorMessage = 'An error has occurred while establishing a connection with the database. Please, try again.'
                return render_template("register.html", errorMessage=errorMessage), 500

            if exists:
                errorMessage = 'The username is already taken. Please, try again.'
                return render_template("register.html", errorMessage=errorMessage), 409

            try:
                exists = cursor.execute(f"SELECT email FROM users WHERE email = '{email}'")
                exists = cursor.fetchone()
            except:
                errorMessage = 'An error has occurred while establishing a connection with the database. Please, try again.'
                return render_template("register.html", errorMessage=errorMessage), 500

            if exists:
                errorMessage = 'The email is already in use. Please, try again, or '
                return render_template("register.html", errorMessage=errorMessage, emailExists=True), 409

            hashedPassword = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

            try:
                cursor.execute(
                    f"INSERT INTO users (username, email, hash) VALUES ('{username}', '{email}', '{hashedPassword}')")
                connection.commit()
                userId = cursor.execute(f"SELECT id FROM users WHERE username = '{username}'")
                userId = cursor.fetchone()
                connection.close()
            except:
                errorMessage = 'An error has occurred while establishing a connection with the database. Please, try again.'
                return render_template("register.html", errorMessage=errorMessage), 500

            session["userId"] = userId[0]
            return redirect("/")

    return render_template("register.html"), 200