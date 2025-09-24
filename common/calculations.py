import cv2
import numpy


def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    opencv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def variance_of_laplacian_quadrants(image):
    height, width = image.size

    # left, top, right, bottom
    top_left_quad = image.crop((0, 0, width / 2, height / 2))
    top_right_quad = image.crop((width / 2, 0, width, height / 2))
    bottom_left_quad = image.crop((0, height / 2, width / 2, height))
    bottom_right_quad = image.crop((width / 2, height / 2, width, height))
    center = image.crop((width / 8, height / 8, (width / 8) * 7, (height / 8) * 7))

    quads = [top_left_quad, top_right_quad, bottom_left_quad, bottom_right_quad, center]

    sum = 0
    vols = ''
    for quad in quads:
        vol = variance_of_laplacian(quad)
        sum += vol
        vols = vols + str(vol) + ' '

    avg = sum / len(quads)

    return avg