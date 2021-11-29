def getUser(db):
	user = db.execute("SELECT * FROM users WHERE id = ?", session.get("user_id"))
	
	return user