"""Utilities for use across apps."""
from db_manager.models import get_session_collection
import datetime
import os
from django.conf import settings
import hashlib


def check_session_active():
    """Check if there is any active session."""
    session_collection = get_session_collection()
    filter_criteria = {
        "created_at": {
            "$gt": datetime.datetime.now()
            - datetime.timedelta(seconds=settings.DEMO_CONSTANTS.demo_time)
        },
        "stopped": 0,
    }
    session = session_collection.find_one(filter_criteria)
    return session


def handle_uploaded_file(f, name):
    """Save uploaded file with given name."""
    if not os.path.exists(settings.DATA_FOLDER):
        os.makedirs(settings.DATA_FOLDER)
    data_path = os.path.join(settings.DATA_FOLDER, "{}".format(name))
    print(data_path)
    with open(data_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return data_path


def get_hashed_mac(mac):
    """Hash mac with salt and take sha1 of the salt."""
    if settings.DEMO_CONSTANTS.use_hashing:
        return hashlib.md5(
            (mac + settings.DEMO_CONSTANTS.salt).encode("utf8")
        ).hexdigest()
    return mac


def get_expiry_date():
    """Get expiry date."""
    date = datetime.date.today() + datetime.timedelta(days=1)
    time = datetime.time(0, 1, 0)
    expiry_date = datetime.datetime.combine(date, time).replace(
        tzinfo=datetime.timezone.utc
    )
    return expiry_date
