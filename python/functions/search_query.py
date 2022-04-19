from Flask import request, redirect

def searchQuery():
    search = request.form.get("search")
    return redirect(f"/search?q={search}")