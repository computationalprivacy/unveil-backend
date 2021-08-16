"""Utils for display manager"""
from constants import (
    DEVICE_ID,
    DEVICE_PIN,
    SHOW_DEVICE_INFO,
    SHOW_DNS_QUERIES,
    SHOW_SECURE_INTERNET_TRAFFIC,
    SHOW_UNSECURE_INTERNET_TRAFFIC,
    DIFFERENTIATE_TRACKERS,
    SHOW_DEVICE,
    DEVICE_POSITION,
)

"""
[
    {
        "device_id": str,
        "device_pin": int,
        "show_device_info": bool,
        "show_dns_queries": bool,
        "show_secure_internet_traffic": bool,
        "show_unsecure_internet_traffic": bool,
        "differentiate_trackers": bool,
        "show_device": bool,
        "device_position": int,
    },
    ...,
]
"""


def generate_filters(
    device_id,
    device_pin,
    show_device_info=False,
    show_dns_queries=False,
    show_secure_internet_traffic=False,
    show_unsecure_internet_traffic=False,
    differentiate_trackers=False,
    show_device=False,
    device_position=-1,
):
    return {
        DEVICE_ID: device_id,
        DEVICE_PIN: device_pin,
        SHOW_DEVICE_INFO: show_device_info,
        SHOW_DNS_QUERIES: show_dns_queries,
        SHOW_SECURE_INTERNET_TRAFFIC: show_secure_internet_traffic,
        SHOW_UNSECURE_INTERNET_TRAFFIC: show_unsecure_internet_traffic,
        DIFFERENTIATE_TRACKERS: differentiate_trackers,
        SHOW_DEVICE: show_device,
        DEVICE_POSITION: device_position,
    }
