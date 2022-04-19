# General app config
app.config["TEMPLATES_AUTO_RELOAD"] = True # Ensure templates are auto-reloaded
app.config['ENV'] = 'development' # Set app's environment to 'development'. Change back again to 'production' when needed
app.config['SECRET_KEY'] = {{ secretKey }} # Set secret key for securely signing session cookies
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True # For formatted jsonify responses for a better human reading
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # Max amount of bytes for file uploading (2 MB)