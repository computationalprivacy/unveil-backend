from adblockparser import AdblockRules
from ap_manager.analyzer.easy_list_scraper import EasyListScrapper

import time


class SingletonMetaClass(type):
    __instance = None

    def __call__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
        return cls.__instance


class EasyListChecker(metaclass=SingletonMetaClass):
    def __init__(self):
        self.bloc_rules = AdblockRules(self.get_rules())
        # self.update_block_rules()

    @staticmethod
    def get_rules():
        return EasyListScrapper().get_rules()

    def update_block_rules(self):
        self.bloc_rules = AdblockRules(self.get_rules())

    def check_url(self, url):
        return self.bloc_rules.should_block(url=url)


if __name__ == "__main__":
    for i in range(1, 10):
        start = time.time()
        EasyListChecker().check_url("ads.example.com")
        end = time.time()
        print(f"Difference {end - start}")
