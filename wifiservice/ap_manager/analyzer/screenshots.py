"""Test screenshots."""
import base64
import os
import traceback
import hashlib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


WINDOW_SIZE = "1920,1080"
DRIVER = 'chromedriver'
MAX_SCREENSHOTS_PER_DEVICE = 10


def save_ss(url):
    """Save screenshot."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

    """Save a screenshot from spotify.com in current directory."""
    driver = webdriver.Chrome(DRIVER, options=chrome_options)
    driver.get(url)
    path = 'imgs/{}.png'.format(
        hashlib.md5(base64.urlsafe_b64encode(
            bytearray(url, 'utf-8'))).hexdigest())
    driver.save_screenshot(path)
    driver.quit()
    b64encoded_image = None
    with open(path, 'rb') as fp:
        b64encoded_image = base64.b64encode(fp.read())
    os.remove(path)
    return b64encoded_image


def get_screenshots(data):
    image_details = []
    for datum in data:
        num_screenshots = 0
        for sess in datum['Internet_Traffic']:
            if num_screenshots > MAX_SCREENSHOTS_PER_DEVICE:
                break
            if sess[2] == 'HTTP':
                try:
                    b64encoded = save_ss(sess[1])
                    image_details.append([
                        b64encoded.decode('utf-8'), sess[1],
                        datum['Device_Info']['MAC Address']])
                    num_screenshots += 1
                except Exception:
                    print("Exception for {}".format(sess))
                    traceback.print_exc()
    return image_details
