"""Create db scraping data from wifispc."""
import json
import glob
import requests
import more_itertools as mit
from pymongo import MongoClient
import progressbar


def wifispc_scraping(
    min_long=-4.145883083343500,
    max_long=1.733506560300000,
    increament=0.1,
    min_lat=45.833381652832000,
    max_lat=58.553176879883000,
):
    """Scrape data from wifispc.

    input: increment, min and max values for longitude and latitude,
        default to UK
    output: dict, keys: nwid names, values: set of corresponding lat,
        lon coordinates
    this functioon creates multiple json files according to found data
    if wifi point already exists in one of the json files
    (has same nwid and lon, lan), it will not be added again.
    """
    nwid_dict = {}
    index = 0
    for longitude in mit.numeric_range(min_long, max_long, increament):
        bar = progressbar.ProgressBar()
        for latitude in bar(mit.numeric_range(min_lat, max_lat, increament)):
            index += 1
            url = (
                "https://wifispc.com/api/index.php?access_token=adiua;"
                "rgjk785(dfb79a7bfba42efedfb472f59f8b79ee7b4bd3iutqb))P"
                "{{FKKv;lkd;ksgo&act=getAllNeighbours&lat={}&lng={}&rad"
                "ius=1&_=1531407940585".format(latitude, longitude)
            )
            r = requests.get(url, allow_redirects=True)
            # r.content is a string, using JSON library to convert it
            json_object = json.loads(r.content)
            valid_wifi = []
            # checks for each wifi point if an ssid name exists
            if "coordinates" in json_object:
                for dic in json_object["coordinates"]:
                    # if ssid exists, add to valid list
                    if dic["nwid"]:
                        nwid_set = nwid_dict.setdefault(dic["nwid"], set())
                        if longitude not in nwid_set and latitude not in nwid_set:
                            nwid_set.update([longitude, latitude])
                            print(
                                "nwid=",
                                dic["nwid"],
                                "longitude=",
                                longitude,
                                "latitude=",
                                latitude,
                            )
                            valid_wifi.append(dic)
                json_object["coordinates"] = valid_wifi
                print(index)
                if json_object["coordinates"]:
                    with open("wifispc{}.json".format(index), "w") as outfile:
                        json.dump(json_object, outfile)
    return nwid_dict


def merge_jsons():
    """Merge multiple jsons files to one `merge_file.json`."""
    read_files = glob.glob("wifispc*.json")
    output_list = []

    for f in read_files:
        with open(f, "r") as infile:
            data = json.load(infile)["coordinates"]
        output_list.extend(data)

    with open("merged_file.json", "w") as outfile:
        json.dump(output_list, outfile)


def mongo_db_export_json(merged_file, collection_name, db_name):
    """Export json to mongo db.

    input: str, names of db, collection, and merged_file
    read data from merged file and insert it
    into collection in Mongo
    """
    client = MongoClient("localhost", 27017, username="wifi", password="WiFiUnveIL")
    db = client[db_name]
    collection = db[collection_name]

    with open("{}.json".format(merged_file)) as file:
        file_data = json.load(file)

    collection.insert(file_data)
    client.close()


if __name__ == "__main__":
    # wifispc_scraping(min_long=-124, max_long=-81, min_lat=32, max_lat=48)
    # print('Done Creating Jsons files! :)')
    # merge_jsons()
    # print('Succeessfully created merged_file.json')
    mongo_db_export_json("merged_file", "ssid", "wifi")
