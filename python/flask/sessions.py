from flask import Flask, redirect, session
from functools import wraps

app = Flask(__name__)
app.secret_key={{ secretKey }}

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Decorate routes to require login.
# https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
def loginRequired(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if session.get("userId") is None:
            return redirect("/login")

        return f(*args, **kwargs)

    return decoratedFunction