from Flask import request, redirect

def searchPost():
    search = request.form.get("search")
    return redirect(f"/search?q={search}")