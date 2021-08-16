from db_manager.models import get_tracker_rules_collection
import requests
from bs4 import BeautifulSoup


class EasyListScrapper:
    def __init__(self):
        pass

    @staticmethod
    def get_rules():
        # get rules from easylist
        urls = [
            "https://easylist.to/easylist/easylist.txt",
            "https://easylist.to/easylist/easyprivacy.txt",
            "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=adblockplus&showintro=0",
        ]
        rules = []
        for url in urls:
            response = requests.get(url)

            # parse the html response and split using new lines
            soup = BeautifulSoup(response.text, "html.parser")
            rules.extend(soup.get_text().split("\n"))

        # get tracker rules collection and update list of rules
        tracker_col = get_tracker_rules_collection()

        query = {"_id": 1}
        new_value = {"_id": 1, "rules": rules}

        tracker_col.replace_one(query, new_value, upsert=True)

        # return rules to be parsed
        return rules
