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