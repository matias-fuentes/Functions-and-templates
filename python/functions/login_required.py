from Flask import redirect, session
from functools import wraps

# Decorate routes to require login.
# https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
def loginRequired(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if session.get("userId") is None:
            return redirect("/login")

        return f(*args, **kwargs)
        
    return decoratedFunction