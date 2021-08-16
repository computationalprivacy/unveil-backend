"""Analyze internet traffic."""

import base64
import logging
import os
import traceback
import utils

from constants import (
    DEVICE_INFO,
    DNS_QUERIES,
    INTERNET_TRAFFIC,
    HTTP,
    SENSITIVE,
    HTTPS,
    MAC_ADDRESS,
    MANUFACTURER,
    MODEL_NUMBER,
    USER_AGENT,
    OS_VERSION,
    USER_PIN,
)
from .analyzer import AccessPointDataAnalyzer
from .analyzer.analyzer import NOT_AVAILABLE
from .analyzer.screenshots import save_ss
from ap_manager.models import Screenshot, Device, Connection, DNSQuery, Filters, Session
from django_rq import job

_LOGGER = logging.getLogger(__name__)


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
    for key, val in dev[DEVICE_INFO].items():
        if val != NOT_AVAILABLE:
            rating += 5
    dns_rating = 0
    for dns, imp in dev[DNS_QUERIES]:
        if utils.dns_sensitivity.is_dns_sensitive(dns):
            dns_rating += 0.5
    rating += min(dns_rating, 50)
    traffic_rating = 0
    for conn in dev[INTERNET_TRAFFIC]:
        if conn[2] == HTTP:
            traffic_rating += 1
        else:
            traffic_rating += 0.5
    rating += min(traffic_rating, 25)
    return rating


def rate_result_orm(device):
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
    if device.manufacturer != NOT_AVAILABLE:
        rating += 5
    if device.model_number != NOT_AVAILABLE:
        rating += 5
    if device.user_agent != NOT_AVAILABLE:
        rating += 5
    if device.os_version != NOT_AVAILABLE:
        rating += 5
    dns_rating = 0
    sensitive_urls = device.dns_queries.all().filter(type=SENSITIVE).count()
    dns_rating += sensitive_urls * 0.5
    rating += min(dns_rating, 50)
    traffic_rating = 0
    traffic_http = device.traffic.all().filter(type=HTTP).count()
    traffic_https = device.traffic.all().filter(type=HTTPS).count()
    traffic_rating += traffic_http + 0.5 * traffic_https
    rating += min(traffic_rating, 25)
    return rating


@job("screenshots")
def generate_new_screenshots(session_id):
    connections = set(
        Connection.objects.filter(type=HTTP)
        .values_list("destination", flat=True)
        .distinct()
    )
    current_screenshots = set(
        Screenshot.objects.values_list("url", flat=True).distinct()
    )
    new_urls = connections - current_screenshots
    session_id_object = Session.objects.get(session_id=session_id)
    for new_url in new_urls:
        try:
            screenshot_base64 = save_ss(new_url)
            if screenshot_base64 is not None:
                Screenshot.objects.create(
                    url=new_url,
                    image=base64.b64decode(screenshot_base64),
                    session_id=session_id_object,
                )
            else:
                Screenshot.objects.create(
                    url=new_url, image=None, session_id=session_id_object
                )
        except Exception:
            traceback.print_exc()
            Screenshot.objects.create(
                url=new_url, image=None, session_id=session_id_object
            )

    return len(new_urls)


@job("data")
def analyze_helper(session_id, data_path):
    packets_analyzer = AccessPointDataAnalyzer()
    results = packets_analyzer(data_path)
    os.remove(data_path)

    try:
        session_id_object = Session.objects.get(session_id=session_id)
    except Session.DoesNotExist:
        raise ValueError

    for device in results:
        data_device, created = Device.objects.get_or_create(
            session_id=session_id_object, mac=device[DEVICE_INFO][MAC_ADDRESS]
        )

        new_manufacturer = device[DEVICE_INFO].get(MANUFACTURER, NOT_AVAILABLE)
        new_model_number = device[DEVICE_INFO].get(MODEL_NUMBER, NOT_AVAILABLE)
        new_user_agent = device[DEVICE_INFO].get(USER_AGENT, NOT_AVAILABLE)
        new_os_version = device[DEVICE_INFO].get(OS_VERSION, NOT_AVAILABLE)
        if not created:
            if new_manufacturer != NOT_AVAILABLE:
                data_device.manufacturer = new_manufacturer if new_manufacturer else data_device.manufacturer
            if new_model_number != NOT_AVAILABLE:
                data_device.model_number = new_model_number if new_model_number else data_device.model_number
            if new_user_agent != NOT_AVAILABLE:
                data_device.user_agent = new_user_agent if new_user_agent else data_device.user_agent
            if new_os_version != NOT_AVAILABLE:
                data_device.os_version = new_os_version if new_os_version else data_device.os_version
        else:
            data_device.manufacturer = new_manufacturer if new_manufacturer else NOT_AVAILABLE
            data_device.model_number = new_model_number if new_model_number else NOT_AVAILABLE
            data_device.user_agent = new_user_agent if new_user_agent else NOT_AVAILABLE
            data_device.os_version = new_os_version if new_os_version else NOT_AVAILABLE
            data_device.pin = device[USER_PIN]
            display_filters = Filters.objects.create(
                device_id=data_device.mac, device_pin=device[USER_PIN]
            )
            data_device.display_filters = display_filters
        data_device.save()
        data_device.traffic.add(
            *[
                Connection.objects.create(
                    time=item[0],
                    destination=item[1],
                    type=item[2],
                    size=item[3],
                    is_tracker=item[4],
                )
                for item in device[INTERNET_TRAFFIC]
            ]
        )
        data_device.dns_queries.add(
            *[
                DNSQuery.objects.create(url=item[0], type=item[1])
                for item in device[DNS_QUERIES]
            ]
        )
        data_device.rating = rate_result_orm(data_device)
        data_device.save()

    generate_new_screenshots.delay(session_id=session_id)
