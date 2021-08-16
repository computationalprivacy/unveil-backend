"""Test screenshots."""
import base64
import tempfile
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import imagehash
from PIL import Image

from constants import DEVICE_INFO, MAC_ADDRESS

WINDOW_SIZE = "1920,1080"
DRIVER = "/usr/bin/chromedriver"
MAX_SCREENSHOTS_PER_DEVICE = 10
WHITE_SCREEN_HASH = "0000000000000000"


def save_ss(url):
    """Save screenshot."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

    """Save a screenshot from spotify.com in current directory."""
    driver = webdriver.Chrome(DRIVER, options=chrome_options)
    driver.get(url)

    with tempfile.NamedTemporaryFile(suffix=".png") as temp:
        driver.save_screenshot(temp.name)
        driver.quit()

        with Image.open(temp.name) as img:
            curr_image_hash = imagehash.average_hash(img)
            if curr_image_hash == imagehash.hex_to_hash(WHITE_SCREEN_HASH):
                return None

        b64encoded_image = base64.b64encode(temp.read())
        return b64encoded_image


def get_screenshots(data, urls_screenshots_created):
    image_details = []
    for datum in data:
        num_screenshots = 0
        for sess in datum["Internet_Traffic"]:
            if num_screenshots > MAX_SCREENSHOTS_PER_DEVICE:
                break
            if sess[2] == "HTTP" and sess[1] not in urls_screenshots_created:
                # f.write(f"Found unsecure website {sess}\n")
                try:
                    b64encoded = save_ss(sess[1])
                    # f.write(f"got screenshot!\n")
                    if b64encoded:
                        image_details.append(
                            [
                                b64encoded.decode("utf-8"),
                                sess[1],
                                datum[DEVICE_INFO][MAC_ADDRESS],
                            ]
                        )
                        num_screenshots += 1

                    urls_screenshots_created.append(sess[1])
                except Exception:
                    # f.write(f"Exception for {traceback.format_exc()}\n")
                    traceback.print_exc()
    return image_details
