@app.route("/logout")
def logout():
    # Forget any userId
    session.clear()
    return redirect("/")