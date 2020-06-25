"""Using WiFiSpc Database to get address."""
import logging
from .ssid_fetcher import SSIDAddFetcher


requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.ERROR)

# method to download json files outside the class


class WifiSpc(SSIDAddFetcher):
    """Assumes Wifispc website was scraped and added in mongodb.

    Attributes:
    db (str), email (str), collection (str): from Config file,
    to be used in Mongodb search and Open Street Map.
    """

    def __init__(self, db_collection):
        """Initialize WifiSpc search class."""
        super(WifiSpc, self).__init__()
        self.collection = db_collection

    def lookup_ssid(self, ssid):
        """Return an SSID via MongoDb db and OpenStreetMap.

        If found ssid in mongodb, returns dic with keys:
        id,address, lat,lng, ssid. If nothing found, returns
        empty dict
        """
        if not ssid:
            raise Exception('Supply SSID to continue')
        # have duplicate ssid's
        cursor = self.collection.find_one(
            {'nwid': ssid}, {'address': 1, 'lat': 1, 'lng': 1, 'nwid': 1})
        if not cursor:
            print("Wifispc No results found for %s" % ssid)
            return {}
        # accesses openmaps API to update dictionary to have city, country keys
        address = self.get_address(
            cursor['lat'], cursor['lng'])
        cursor.update(address)
        cursor['ssid'] = cursor.pop('nwid', ssid)
        cursor.pop('_id', None)
        return cursor
