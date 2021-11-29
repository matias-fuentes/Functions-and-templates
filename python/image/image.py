import os

from PIL import Image
from werkzeug.utils import secure_filename

def allowedImage(image):
    allowedExtensions = set(['png', 'jpg', 'jpeg', 'bmp', 'webp'])
    return '.' in image and image.rsplit('.', 1)[1].lower() in allowedExtensions


def uploadImage(db, image, username, directory):
    if image and allowedImage(image.filename):
	    filename = secure_filename(image.filename)

       	image = Image.open(image)
        image.save(os.path.join(directory, filename))

        db.execute("UPDATE [table] SET image = ? WHERE username = ?", filename, username)
	
	return