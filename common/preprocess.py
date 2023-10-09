import PIL
import numpy


def preprocess_img_for_ml_model(img):
    #img = img.resize((299, 299), PIL.Image.NEAREST)  # Best Speed
    img = img.resize((299, 299), PIL.Image.LANCZOS)  # Best Quality
    img_np = numpy.array(img).astype(numpy.float32)
    return img_np, img