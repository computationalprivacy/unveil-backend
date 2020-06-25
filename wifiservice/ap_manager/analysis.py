"""Analyze internet traffic."""
import datetime
import utils
import os
from .analyzer import AccessPointDataAnalyzer
from .analyzer.analyzer import NOT_AVAILABLE
from db_manager.models import get_internet_data_collection
from .utils import get_sorted_devices
from utils.optout import get_opted_out_mac
from utils.utils import get_hashed_mac, get_expiry_date
from utils.scheduling import get_scheduler, empty_scheduler
from .analyzer.screenshots import get_screenshots
from django_rq import job


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
    for key, val in dev['Device_Info'].items():
        if val != NOT_AVAILABLE:
            rating += 5
    dns_rating = 0
    for dns, imp in dev['DNS_Queries']:
        if utils.dns_sensitivity.is_dns_sensitive(dns):
            dns_rating += 0.5
    rating += min(dns_rating, 50)
    traffic_rating = 0
    for conn in dev['Internet_Traffic']:
        if conn[2] == 'HTTP':
            traffic_rating += 1
        else:
            traffic_rating += 0.5
    rating += min(traffic_rating, 25)
    return rating


def rate_and_insert(
        session_id, results, screenshots, internet_data_collection):
    """Parse results and assign rating."""
    creation_time = datetime.datetime.now()
    res = {
        'session_id': session_id,
        'creation_time': creation_time,
        'results': results,
        'screenshots': screenshots}
    for dev in res['results']:
        # if 'rating' in dev:
        #     dev.pop('rating', None)
        if 'rating' not in dev:
            dev['rating'] = rate_result(dev)
    res['results'] = get_sorted_devices(res['results'])
    res['rating'] = sum([dev['rating'] for dev in res['results']])
    res['expire_at'] = get_expiry_date()
    internet_data_collection.replace_one(
        {'session_id': res['session_id']}, res, upsert=True)
    return res


def generate_and_insert_screenshots(
        internet_data_collection, session_id, results):
    """Generate and inserts screenshots."""
    print("Results available for AP analysis. Generating screenshots now.")
    screenshots = get_screenshots(results)
    data_filter = {'session_id': session_id}
    available_data = internet_data_collection.find_one(data_filter)
    if available_data:
        screenshots.extend(available_data['screenshots'])
        results = available_data['results']
    update = rate_and_insert(
        session_id, results, screenshots, internet_data_collection)
    return update


@job('data')
def analyze_helper(session_id, data_path):
    """Analyze helper."""
    internet_data_collection = get_internet_data_collection()
    packets_analyzer = AccessPointDataAnalyzer()
    results = packets_analyzer(data_path)
    data_filter = {'session_id': session_id}
    available_data = internet_data_collection.find_one(data_filter)
    screenshots = []
    # if len(analysis_results) == 0:
    #     os.remove(data_path)
    os.remove(data_path)
    if available_data:
        results.extend(available_data['results'])
        screenshots = available_data['screenshots']
    res = rate_and_insert(
        session_id, results, screenshots, internet_data_collection)
    res = generate_and_insert_screenshots(
        internet_data_collection, session_id, results)
    return res['rating']


def remove_opt_out_users():
    """Remove opted out users from dataset if available."""
    print("Removing opt out users.")
    opt_out_mac = get_opted_out_mac()
    mac_list = [get_hashed_mac(mac) for mac in opt_out_mac]
    internet_data_collection = get_internet_data_collection()
    analysis_results = list(internet_data_collection.find())
    for res in analysis_results:
        filtered_results = [
            dev for dev in res['results'] if
            dev['Device_Info']['MAC Address'] not in mac_list]
        res['results'] = filtered_results
        rate_and_insert(
            res['session_id'], filtered_results, res['screenshots'],
            internet_data_collection)


def schedule_optout():
    """Schedule removal of opt out users."""
    scheduler = get_scheduler()
    empty_scheduler(exclude_optout=False)
    schedule_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
    scheduler.schedule(
        scheduled_time=schedule_time,
        func=remove_opt_out_users,
        args=None,
        kwargs=None,
        interval=900,
        repeat=None,
        result_ttl=1000  # should be greater than interval
    )
