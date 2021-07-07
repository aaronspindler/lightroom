import time
from io import BytesIO

import requests
from PIL import Image
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import config

WAIT_TIME = 2


def main():
    # Setup the web driver
    driver = webdriver.Safari()
    driver.get('https://lightroom.adobe.com/signin')
    driver.set_window_size(2000, 1200)

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
    time.sleep(WAIT_TIME * 2)
    enable_cookies_button = driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
    time.sleep(WAIT_TIME)

    # Click into the all photos tab
    all_photos_button = driver.find_element_by_xpath('//*[@id="ze-sidebar-all-photos"]/div[1]/span[2]').click()

    # Click on the first image to expand it
    first_image_tile = driver.find_elements_by_class_name('image')[0].click()
    time.sleep(WAIT_TIME)

    # Set requests cookies from webdriver
    s = requests.Session()
    for cookie in driver.get_cookies():
        s.cookies.set(cookie['name'], cookie['value'])

    # Loop through the catalog of images
    for _ in range(50):
        # Find the correct image
        div_tag = driver.find_element_by_class_name('ze-active')
        play_icon = div_tag.find_element_by_class_name('play')
        if play_icon.get_attribute('style') != 'display: none;':
            print('VIDEO')
        else:
            img = div_tag.find_element_by_tag_name('img')
            img_src = img.get_attribute('src')
            response = s.get(img_src)
            img = Image.open(BytesIO(response.content))
            print(img.size)
            time.sleep(1)
        driver.find_element_by_xpath('/html/body/sp-theme').send_keys(Keys.RIGHT)


if __name__ == '__main__':
    main()

