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