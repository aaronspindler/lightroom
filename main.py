import time
import uuid
import config
from io import BytesIO

import PIL
import coremltools as ct
import cv2
import numpy
import numpy as np
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

WAIT_TIME = 2


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


def preprocess_img_for_ml_model(img):
    #img = img.resize((299, 299), PIL.Image.NEAREST)  # Best Speed
    img = img.resize((299, 299), PIL.Image.LANCZOS)  # Best Quality
    img_np = np.array(img).astype(np.float32)
    return img_np, img


def main():
    print('lightroom-blur')
    # Load the Image Model
    model = ct.models.MLModel('BlurDetection.mlmodel')
    print('Loaded ML model')

    # Setup the web driver
    driver = webdriver.Safari()
    driver.get('https://lightroom.adobe.com/signin')
    driver.set_window_size(2000, 1200)
    print('Loaded webdriver')

    time.sleep(WAIT_TIME)

    # Login
    email_field = driver.find_element_by_xpath('//*[@id="EmailPage-EmailField"]')
    email_field.send_keys(config.LIGHTROOM_EMAIL)
    time.sleep(WAIT_TIME)
    continue_button = driver.find_element_by_xpath('//*[@id="EmailForm"]/section[2]/div[2]/button/span').click()
    time.sleep(WAIT_TIME)
    password_field = driver.find_element_by_xpath('//*[@id="PasswordPage-PasswordField"]')
    password_field.send_keys(config.LIGHTROOM_PASSWORD)
    continue_button = driver.find_element_by_xpath('//*[@id="PasswordForm"]/section[2]/div[2]/button/span').click()
    try:
        driver.find_element_by_xpath('//*[@id="App"]/div/div/section/div/div/section/div/section/div/div/section/footer/div/button/span').click() # Look for a 'Want to sign in without your password?' screen and then clck 'Skip and Continue'
    except:
        pass
    print('Finished login process')
    time.sleep(WAIT_TIME * 2)
    enable_cookies_button = driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
    time.sleep(WAIT_TIME)

    # Click into the all photos tab
    all_photos_button = driver.find_element_by_xpath('//*[@id="ze-sidebar-all-photos"]/div[1]/span[2]').click()

    # Click on the first image to expand it
    first_image_tile = driver.find_elements_by_class_name('image')[0].click()
    time.sleep(WAIT_TIME)

    # Set requests cookies from webdriver
    # These allow us to access the current photo directly from a python web request
    s = requests.Session()
    session_counter = 0
    for cookie in driver.get_cookies():
        session_counter += 1
        s.cookies.set(cookie['name'], cookie['value'])
    print(f'Set {session_counter} cookies')

    # Loop through the catalog of images
    # Find the number of images
    time.sleep(WAIT_TIME)
    countlabel = driver.find_element_by_class_name('countlabel').text
    num_images = int(countlabel.split(' ')[2])
    print(f'Found {num_images} files')

    # initialize some stats
    time_start = time.time()
    num_processed = 0
    num_blurred = 0
    num_duplicate = 0
    images = {}

    print('Started processing images')
    # for _ in range(num_images):
    for _ in range(200):
        # Find the correct image
        div_tag = driver.find_element_by_class_name('ze-active')
        play_icon = div_tag.find_element_by_class_name('play')
        if play_icon.get_attribute('style') != 'display: none;':
            print(f'{"video":11s} {round(1.00, 2) * 100:6.2f}%')
            pass  # Pass since it is a video, and we don't process videos
        else:
            num_processed += 1
            img = div_tag.find_element_by_tag_name('img')
            img_src = img.get_attribute('src')
            response = s.get(img_src)

            # Convert the response data into a PIL image
            pil_img = Image.open(BytesIO(response.content)).convert('RGB')

            # Compute the hash of the image
            hash = img_hash(pil_img)
            if hash in images:
                num_duplicate += 1
                # driver.find_element_by_xpath('//*[@id="sneaky-loupe-rating"]/div/div[1]').click()  # Click the 1 star button so I can find duplicates
            else:
                images[hash] = pil_img

            # Make Prediction with Ml model
            _, img = preprocess_img_for_ml_model(pil_img)
            prediction_result = model.predict({'image': img})
            print(f'{prediction_result.get("classLabel"):11s} {round(prediction_result.get("classLabelProbs").get(prediction_result.get("classLabel")), 2) * 100:6.2f}%')

            if prediction_result.get('classLabel') == 'blurred':
                num_blurred += 1
                # driver.find_element_by_xpath('//*[@id="sneaky-loupe-flag"]/div[2]').click()  # Click the flag as reject button

            # Make decision based on V o l quadrants
            quadrants = variance_of_laplacian_quadrants(pil_img)

            # Make decision based on V o l
            vol = variance_of_laplacian(pil_img)

            # print(f'Quads: {quadrants} VoL: {vol}')
            descriptor = ''
            if vol < 100:
                descriptor = 'BLUR'
                # pil_img.save(f'/Users/aaronspindler/Desktop/lightroom-blur/images/blur/{uuid.uuid4().hex}.jpg', 'JPEG') # Saves the blurry image to a folder with unique filename

        # Press the right key to move to the next image
        driver.find_element_by_xpath('/html/body/sp-theme').send_keys(Keys.RIGHT)

    time_end = time.time()
    time_elapsed = round(time_end - time_start, 2)
    print(f'Processed {num_processed} images in {time_elapsed} seconds ({round(num_processed / time_elapsed, 2)} img/s)')

    print(f'{num_blurred} blurry pictures')
    print(f'{num_duplicate} duplicate pictures')


if __name__ == '__main__':
    main()
