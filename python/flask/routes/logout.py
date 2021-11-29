from Flask import session, redirect

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    return redirect("/")