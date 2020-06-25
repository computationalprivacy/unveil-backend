"""Test screenshots."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import base64
import os


WINDOW_SIZE = "1920,1080"


data = None
with open('data.json') as fp:
    data = json.load(fp)


def save_ss(url):
    """Save screenshot."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

    """Save a screenshot from spotify.com in current directory."""
    DRIVER = 'chromedriver'
    driver = webdriver.Chrome(DRIVER, options=chrome_options)
    driver.get(url)
    path = 'imgs/{}.png'.format(
        base64.urlsafe_b64encode(bytearray(url, 'utf-8')).decode('utf-8'))
    driver.save_screenshot(path)
    driver.quit()
    with open(path, 'rb') as fp:
        return base64.b64encode(fp.read())


def create_images():
    image_details = []
    for datum in data:
        for sess in datum['Internet_Traffic']:
            if sess[2] == 'HTTP':
                print(sess[1])
                b64encoded = save_ss(sess[1])
                image_details.append(
                    [b64encoded.decode('utf-8'), sess[1],
                     datum['Device_Info']['MAC Address']])

    with open('images.json', 'w') as fp:
        json.dump(image_details, fp)


def name_to_url():
    """Convert name to url."""
    name_list = os.listdir('imgs')
    for name in name_list:
        name = os.path.splitext(name)[0]
        print(base64.urlsafe_b64decode(bytearray(name, 'utf-8')).decode('utf-8'))


create_images()
