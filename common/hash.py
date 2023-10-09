import cv2
import numpy

def img_hash(img, hashsize=8):
    # convert the image to grayscale so the hash is only on one channel
    opencv_image = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    # resize the input image, adding a single column (width) so we
    # can compute the horizontal gradient
    resized = cv2.resize(gray, (hashsize + 1, hashsize))
    # compute the (relative) horizontal gradient between adjacent
    # column pixels
    diff = resized[:, 1:] > resized[:, :-1]
    # convert the difference image to a hash
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])