import os
import pyrebase

from PIL import Image
from werkzeug.utils import secure_filename
from webptools import cwebp

# Checks if an image has a valid format (.png, .jpg, .webp)
def validImage(image):
    allowedExtensions = set(['png', 'jpg', 'jpeg', 'webp'])
    return '.' in image and image.rsplit('.', 1)[1].lower() in allowedExtensions


# Crops images to a 1:1 aspect ratio
def cropImage(image):
    width, height = image.size

    if width == height:
        return image

    offset = int(abs(height - width)/2)

    if width > height:
        image = image.crop([offset,0,width-offset,height])
    else:
        image = image.crop([0,offset,width,height-offset])

    return image


# Saves images (banner and profile pictures), keeps a record of the images of each image of each user, and updates the
# uploaded images
def uploadImage(cursor, profilePic, bannerPic, username, connection, firebaseConfig):
    try:
        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
    except:
        message = 'An error has occurred while establishing a connection with the database. Please, try again.'
        return False, message

    profilePicDir = 'static/temp/profilePictures/'
    bannerPicDir = 'static/temp/bannerPictures/'

    if profilePic and bannerPic:
        if validImage(profilePic.filename) and validImage(bannerPic.filename):
            profFilename = secure_filename(profilePic.filename)
            bannFilename = secure_filename(bannerPic.filename)

            image = Image.open(profilePic)
            profilePic = cropImage(image)

            try:
                profilePic.save(os.path.join(profilePicDir, profFilename))
                bannerPic.save(os.path.join(bannerPicDir, bannFilename))
            except:
                message = 'An error has occurred while uploading your photos. Please, try again.'
                return False, message

            formatIndex = profFilename.find('.', len(profFilename) - 5, len(profFilename) - 1)
            profFilenameWebp = profFilename[:formatIndex] + '.webp'
            formatIndex = bannFilename.find('.', len(bannFilename) - 5, len(bannFilename) - 1)
            bannFilenameWebp = bannFilename[:formatIndex] + '.webp'

            cwebp(input_image=profilePicDir + profFilename, output_image=profilePicDir + profFilenameWebp, option='-q 80')
            cwebp(input_image=bannerPicDir + bannFilename, output_image=bannerPicDir + bannFilenameWebp, option='-q 80')

            try:
                storage.child(profFilenameWebp).put(profilePicDir + profFilenameWebp)
                storage.child(bannFilenameWebp).put(bannerPicDir + bannFilenameWebp)
                cursor.execute(
                    f"UPDATE users SET profilePicDir = '{profFilenameWebp}', bannerPicDir = '{bannFilenameWebp}' WHERE username = '{username}'")
                connection.commit()
            except:
                message = 'An error has occurred while uploading your photos. Please, try again.'
                return False, message

            os.remove(profilePicDir + profFilename)
            os.remove(profilePicDir + profFilenameWebp)
            os.remove(bannerPicDir + bannFilename)
            os.remove(bannerPicDir + bannFilenameWebp)

            return True
        else:
            message = 'Error! Allowed image types are: .png, .jpg, and .webp. Please, try again.'
            return False, message

    elif profilePic:
        if validImage(profilePic.filename):
            profFilename = secure_filename(profilePic.filename)
            image = Image.open(profilePic)
            profilePic = cropImage(image)

            try:
                profilePic.save(os.path.join(profilePicDir, profFilename))
            except:
                message = 'An error has occurred while uploading your photos. Please, try again.'
                return False, message

            formatIndex = profFilename.find('.', len(profFilename) - 5, len(profFilename) - 1)
            profFilenameWebp = profFilename[:formatIndex] + '.webp'
            cwebp(input_image=profilePicDir + profFilename, output_image=profilePicDir + profFilenameWebp, option='-q 80')

            try:
                storage.child(profFilenameWebp).put(profilePicDir + profFilenameWebp)
                cursor.execute(
                    f"UPDATE users SET profilePicDir = '{profFilenameWebp}' WHERE username = '{username}'")
                connection.commit()
            except:
                message = 'An error has occurred while uploading your photos. Please, try again.'
                return False, message

            os.remove(profilePicDir + profFilename)
            os.remove(profilePicDir + profFilenameWebp)
            
            return True
        else:
            message = 'Error! Allowed image types are: .png, .jpg, and .webp. Please, try again.'
            return False, message

    else:
        if validImage(bannerPic.filename):
            bannFilename = secure_filename(bannerPic.filename)

            try:
                bannerPic.save(os.path.join(bannerPicDir, bannFilename))
            except:
                message = 'An error has occurred while uploading your photos. Please, try again.'
                return False, message

            formatIndex = bannFilename.find('.', len(bannFilename) - 5, len(bannFilename) - 1)
            bannFilenameWebp = bannFilename[:formatIndex] + '.webp'
            cwebp(input_image=bannerPicDir + bannFilename, output_image=bannerPicDir + bannFilenameWebp, option='-q 80')

            try:
                storage.child(bannFilenameWebp).put(bannerPicDir + bannFilenameWebp)
                cursor.execute(
                    f"UPDATE users SET bannerPicDir = '{bannFilenameWebp}' WHERE username = '{username}'")
                connection.commit()
            except:
                message = 'An error has occurred while uploading your photos. Please, try again.'
                return False, message

            os.remove(bannerPicDir + bannFilename)
            os.remove(bannerPicDir + bannFilenameWebp)
            
            return True
        else:
            message = 'Error! Allowed image types are: .png, .jpg, and .webp. Please, try again.'
            return False, message