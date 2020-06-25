"""Use Wigle API."""
# using median of lon, lat to remove outliers locations
# and extract only one location of the 100 locations list
# Finding the address of only one location
# The following Wigle API user is allowed 500 queries per day
# if ssid empty,  returns dictionary with empty address

import logging
from configparser import ConfigParser
from statistics import median
from requests.auth import HTTPBasicAuth
import requests
from .ssid_fetcher import SSIDAddFetcher
from django.conf import settings


requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.ERROR)


class Wigle(SSIDAddFetcher):
    """Searches Wigle API to output info dict according to ssid_name.

    Attributes:
        user (str), email (str), key (str): from Config file,
        used in Open Strret Map and accessing Wigle API.
    """

    def __init__(self):
        """Initialize wigle data."""
        super(Wigle, self).__init__()
        try:
            user = settings.WIGLE['user']
            key = settings.WIGLE['key']
            self.email = settings.WIGLE['email']
        except Exception:
            raise ValueError(
                'Please enter your API key into the wigle.conf file. '
                'See https://api.wigle.net/')
        if user == "changeme" or key == "changeme" or self.email == "changeme":
            raise ValueError(
                'Please enter your API key into the wigle.conf file. '
                'See https://api.wigle.net/')
        self.auth = HTTPBasicAuth(user, key)

    def average_location(self, locations, ssid, locations_length):
        """Return average location.

        Args:
            param1 (list): locations results from Wigle
            param2 (str): ssid we're looking for
            param3 (int): number of locations
        Returns:
            for locations in the same country:
                one location with avg val for lat and lon
            if no results found, or all locations are form different countries,
            returns empty dict

        """
        # one location
        if locations_length == 1:
            med_lat, med_lon = locations[0]['trilat'], locations[0]['trilong']
        else:  # only check locations in the same country
            countries_lst = [location['country'] for location in locations
                             if location['country']]
            # have duplicates
            if len(set(countries_lst)) != len(countries_lst):
                # get the most freq country
                # calculate median without other countries
                most_freq_country = max(
                    set(countries_lst), key=countries_lst.count)
                med_lat = median(
                    (location['trilat'] for location in locations
                     if location['country'] == most_freq_country))
                med_lon = median(
                    (location['trilong'] for location in locations
                     if location['country'] == most_freq_country))
            else:  # all countries in locations are different
                return {}
        new_location = {
            "shortaddress": "", "city": "", "code": "", "county": "",
            "postcode": "", "road": "", "state": "", "suburb": "",
            "ssid": ssid, "lat": med_lat, "lng": med_lon, "address": ''}
        return new_location

    def lookup_ssid(self, ssid):
        """Lookup an SSID via Wigle and OpenStreetMap.

        input: SSID string, if empty raise an exception
        output: dict of one location, empty if no locations found
        keys: city, code, country, lat, lng, address, postcode, road,
        shortaddress, ssid, state, suburb
        """
        if not ssid:
            raise Exception('Supply SSID to continue')
        r = requests.get(
            "https://api.wigle.net/api/v2/network/search?first=0&"
            "freenet=false&paynet=false&ssid=%s" % ssid, auth=self.auth)
        if r.status_code != 200:
            logging.error(
                "Unable to lookup %s, bad status: %d. "
                "Have you set your API keys correctly?" % (
                    ssid, r.status_code))
            return
        try:
            # Depending on package version json is either a function or a
            # value. FML.
            result = r.json()
        except Exception:
            try:
                # Depending on package version json is either a function or a
                # value. FML.
                result = r.json
            except Exception as e:
                logging.error("Unable to decode JSON response for %s" % ssid)
                logging.error(e)
                return

        locations = result.get('results')
        # no results found
        if not locations:
            print("Wigle - No results found for %s" % ssid)
            return {}
        filtered_location = self.average_location(
            locations, ssid, len(locations))
        # accesses openmaps API to update address
        if filtered_location:
            address = self._get_address(
                filtered_location['lat'], filtered_location['lng'])
            filtered_location.update(address)
        else:
            print("Wigle - No results found for %s" % ssid)
            return {}
        return filtered_location
