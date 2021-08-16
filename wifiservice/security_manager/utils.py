from random import randint

from django.conf import settings

from ap_manager import models
from ap_manager.utils import get_sorted_devices
from django.http import JsonResponse
from jwt import encode
from security_manager.models import User
from utils.utils import get_hashed_mac


def generate_orm_session_results(request, session_id, filtered=False):
    if filtered:
        device = models.Device.objects.get(mac=request.mac_address)
        results = (
            [device.to_json()] if device and device.display_filters.show_device else []
        )
    else:
        results = [
            device.to_json()
            for device in models.Device.objects.filter(
                session_id__session_id=session_id
            )
            if device.display_filters.show_device
        ]
        results = get_sorted_devices(results)
    return JsonResponse({"results": results})


def generate_orm_session_results_screen(session_id, data_screen):
    result = [
        device.to_json()
        for device in models.Device.objects.filter(
            session_id__session_id=session_id,
            display_filters__device_position=data_screen,
            display_filters__show_device=True,
        ).all()
    ]

    return JsonResponse({"results": result})


def register_user(mac_address):
    pin = generate_pin_code()
    hash_mac = get_hashed_mac(mac_address)
    return User.objects.create(
        user_pin=pin, mac_address=hash_mac, mac_address_unhashed=mac_address
    )


def generate_pin_code():
    return randint(10000, 99999)


def verify_login(user_pin):
    user = User.objects.filter(user_pin=user_pin).first()
    return user.pk if user is not None else None


def generate_jwt_token(userid):
    user = User.objects.get(pk=userid)
    mac = user.mac_address
    token = encode(
        payload={"user_pin": userid, "hash": mac},
        key=settings.SECRET_KEY,
        algorithm="HS256",
    ).decode("utf-8")
    return token
