from PIL import Image

def cropImage(image):
    width, height = image.size

    if width == height:
        return image

    offset = int(abs(height-width)/2)

    if width > height:
        image = image.crop([offset,0,width-offset,height])
    else:
        image = image.crop([0,offset,width,height-offset])

    return image