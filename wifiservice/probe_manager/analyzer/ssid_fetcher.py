"""Generic SSID address fetcher."""
import requests
import logging
import json


class SSIDAddFetcher(object):
    """SSID Add fetcher abstract class."""

    def __init__(self):
        """Initialize class."""
        pass

    def _get_address(self, gps_lat, gps_long):
        """Get street address from GPS coordinates."""
        lookup_url = (
            "http://nominatim.openstreetmap.org/reverse?zoom=18&"
            "addressdetails=1&format=json&email=%s&lat=%s&lon=%s&accept-"
            "language=en" % (self.email, gps_lat, gps_long)
        )
        try:
            req = requests.get(lookup_url)
            if req.status_code == 200 and "json" in req.headers["content-type"]:
                # addj = json.loads(req.text.encode('UTF8'))
                addj = json.loads(req.text.encode("utf-8"))
                latitude = addj.get("lat", gps_lat)
                longitude = addj.get("lon", gps_long)
                longaddress = addj.get("display_name", "")
                compound_address = addj.get("address", {})
                city = compound_address.get("city", "")
                country = compound_address.get("country", "")
                country_code = compound_address.get("country_code", "")
                county = compound_address.get("county", "")
                postcode = compound_address.get("postcode", "")
                housenumber = compound_address.get("house_number", "")
                road = compound_address.get("road", "")
                state = compound_address.get("state", "")
                suburb = compound_address.get("suburb", "")
                shortaddress = "%s %s, %s" % (housenumber, road, city)
                shortaddress = shortaddress.strip()
            return {
                "lng": longitude,
                "lat": latitude,
                "address": longaddress,
                "shortaddress": shortaddress,
                "city": city,
                "country": country,
                "code": country_code,
                "county": county,
                "postcode": postcode,
                "road": road,
                "state": state,
                "suburb": suburb,
            }
        except Exception as e:
            logging.error(
                "Unable to retrieve address from OpenStreetMap - '{}'".format(str(e))
            )

    def lookup_ssid(self, ssid):
        """Must be implemented in child class."""
        raise NotImplementedError
