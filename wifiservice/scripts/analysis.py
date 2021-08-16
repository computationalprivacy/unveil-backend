"""Analyze internet traffic."""
import datetime


def rate_result(dev):
    """Rate result for a device.

    Each new device is rated on scale of 100

    Device details - 25
    Internet Traffic - 25
        1 x number of  HTTP requests + 0.5 x number of HTTPS requests
    DNS Queries - 50
        0 for generic queries like - whatsapp, skype, microsoft, facebook,
            akamaiedge, linkedin, twitter, apple
        0.5 for everything else
    """
    rating = 0
    for key, val in dev["Device_Info"].items():
        if val != NOT_AVAILABLE:
            rating += 5
    dns_rating = 0
    for dns, imp in dev["DNS_Queries"]:
        if utils.dns_sensitivity.is_dns_sensitive(dns):
            dns_rating += 0.5
    rating += min(dns_rating, 50)
    traffic_rating = 0
    for conn in dev["Internet_Traffic"]:
        if conn[2] == "HTTP":
            traffic_rating += 1
        else:
            traffic_rating += 0.5
    rating += min(traffic_rating, 25)
    return rating


def get_sorted_devices(dev_list):
    """Return sorted devices."""
    return sorted(dev_list, key=lambda k: k["rating"], reverse=True)


def assign_dev_rating(res):
    """Parse results and assing rating."""
    for dev in res["results"]:
        # if 'rating' in dev:
        #     dev.pop('rating', None)
        if "rating" not in dev:
            dev["DNS_Queries"] = packets_analyzer.sanitize_dns(dev["DNS_Queries"])
            dev["rating"] = rate_result(dev)
    res["results"] = get_sorted_devices(res["results"])
    res["rating"] = sum([dev["rating"] for dev in res["results"]])
    return res


def analyze_helper(data_path):
    """Analyze helper."""
    creation_time = datetime.datetime.now()
    analysis_results = packets_analyzer(data_path)
    res = {
        "session_id": session_id,
        "path": data_path,
        "creation_time": creation_time,
        "results": analysis_results,
    }
    res = assign_dev_rating(res)
    update = internet_data_collection.replace_one({"path": data_path}, res, upsert=True)
