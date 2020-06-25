"""Classes for database."""
from pymongo import MongoClient
from django.conf import settings


class MongoConnection(object):
    """Create a Mongo connection to the database."""

    def __init__(self):
        """Initialize mongo collection."""
        client = MongoClient(
            settings.MONGO_DB['host'],
            settings.MONGO_DB['port'],
            password=settings.MONGO_DB['password'],
            username=settings.MONGO_DB['username'])
        self.db = client[settings.MONGO_DB['db_name']]

    def get_collection(self, name):
        """Return specified collection."""
        return self.db[name]


def get_display_collection():
    """Return display collection."""
    return MongoConnection().get_collection('display')


def get_public_ap_collection():
    """Return public ap collection."""
    return MongoConnection().get_collection('public_ap')


def get_internet_data_collection():
    """Return internet data collection."""
    coll = MongoConnection().get_collection('internet_analysis')
    coll.create_index("expire_at", expireAfterSeconds=0)
    return coll


def get_optout_collection():
    """Return collection of MAC addresses who have opted out."""
    return MongoConnection().get_collection('optout')


def get_session_collection():
    """Return collection of sessions."""
    return MongoConnection().get_collection('sessions')


def get_instructions_collection():
    """Return collection of instructions for each pi."""
    return MongoConnection().get_collection('instructions')


def get_status_collection():
    """Return status collection."""
    return MongoConnection().get_collection('status')


def get_ssid_collection():
    """Return ssid collection."""
    return MongoConnection().get_collection('ssid')


def get_probe_analysis_collection():
    """Return probe analysis collection."""
    coll = MongoConnection().get_collection('probe_analysis')
    coll.create_index("expire_at", expireAfterSeconds=0)
    return coll
