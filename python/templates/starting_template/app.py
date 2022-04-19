# My own packages
from image import uploadImage
from search_query import searchQuery
from login_required import loginRequired
from db import validateUser, createPool, getUsername, getProfile, query

# Third-party packages
from re import fullmatch
from werkzeug.security import generate_password_hash
from flask import Flask, render_template, session, request, redirect

poolData = {
    "poolName": {{ poolName }},
    "host": {{ host }},
    "port": {{ port }},
    "user": {{ user }},
    "password": {{ password }},
    "db": {{ db }}
}
pool = createPool(poolData)

# We initialize the Flask app
app = Flask(__name__)

# General app config
app.config["TEMPLATES_AUTO_RELOAD"] = True # Ensure templates are auto-reloaded
app.config['SECRET_KEY'] = {{ secretKey }} # Set secret key for securely signing session cookies
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # Max amount of bytes for file uploading (2 MB)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True # For formatted jsonify responses for a better human reading
app.config['ENV'] = 'development' # Set app's environment to 'development'. Change back again to 'production' when needed

# Regexes for input validation
userRegEx = '[A-Za-z0-9._-]{3,16}'
passRegEx = '[A-Za-z0-9¡!¿?$+._-]{6,16}'
emailRegEx = '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    return response


@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")


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


@app.route("/logout")
def logout():
    # Forget any userId
    session.clear()
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@loginRequired
def profile():
    try:
        errorMessage = 'An error has occurred while establishing a connection with the database. Please, try again.'
        connection = pool.get_connection()
        cursor = connection.cursor()

        userId = session.get("userId")
        username = getUsername(cursor, userId)

        if not username:
            raise Exception(errorMessage)
    except:
        return render_template("profile.html", errorMessage=errorMessage), 500
    
    if request.method == "POST":
        profilePic = request.files['profilePic']
        bannerPic = request.files['bannerPic']
        if profilePic or bannerPic:
            firebaseConfig = {
                "apiKey": {{ firebaseApiKey }},
                "authDomain": {{ authDomain }},
                "projectId": {{ projectId }},
                "storageBucket": {{ storageBucket }},
                "messagingSenderId": {{ messagingSenderId }},
                "appId": {{ appId }},
                "measurementId": {{ measurementId }},
                "serviceAccount": {
                        "type": {{ serviceAccountType }},
                        "project_id": {{ projectId }},
                        "private_key_id": {{ privateKeyId }},
                        "private_key": {{ privateKey.replace('\\n', '\n') }},
                        "client_email": {{ clientEmail }},
                        "client_id": {{ clientId }},
                        "auth_uri": {{ authUri }},
                        "token_uri": {{ tokenUri }},
                        "auth_provider_x509_cert_url": {{ authProviderx509CertURL }},
                        "client_x509_cert_url": {{ clientx509CertURL }}
                    },
                "databaseURL": {{ databaseURL }}
            }

            uploaded, message = uploadImage(cursor, profilePic, bannerPic, username, connection, firebaseConfig)
            picDirectory = getProfile(cursor, userId)
            connection.close()

            if picDirectory == False:
                errorMessage = 'An error has occurred while fetching your profile info. Please, try again.'
                return render_template("profile.html", errorMessage=errorMessage, userId=userId, username=username), 500

            if (uploaded):
                successfulMessage = 'The images have been uploaded successfully.'
                return render_template("profile.html", successfulMessage=successfulMessage, picDirectory=picDirectory,
                    userId=userId, username=username), 200

            else:
                return render_template("profile.html", errorMessage=message, picDirectory=picDirectory,
                    userId=userId, username=username), 422

    picDirectory = getProfile(cursor, userId)
    connection.close()

    if picDirectory == False:
        errorMessage = 'An error has occurred while loading your profile info. Please, try again.'
        return render_template("profile.html", errorMessage=errorMessage, userId=userId, username=username), 500
        
    return render_template("profile.html", picDirectory=picDirectory, username=username, userId=userId), 200


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        return searchQuery()
    else:
        try:
            errorMessage = 'An error has occurred while establishing a connection with the database. Please, try again.'
            connection = pool.get_connection()
            cursor = connection.cursor()

            username = getUsername(cursor)
            connection.close()

            if not username:
                raise Exception(errorMessage)
        except:
            return render_template("search.html", errorMessage=errorMessage), 500

        q = request.args.get('q')
        response = query(q)
        return render_template("search.html", response=response, userId=session.get("userId"), username=username)