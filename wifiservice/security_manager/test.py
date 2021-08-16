"""Tests for consent registration endpoint."""

from django.test import Client, LiveServerTestCase
from django.urls import reverse

from security_manager import models
from utils.utils import get_hashed_mac


class ConsentRegisterTests(LiveServerTestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.device_1_mac = "04:d6:aa:15:b8:b0"
        self.device_2_mac = "fe:40:d9:b4:fd:d2"

    def test_register(self):
        mac_address = self.device_1_mac
        response = self.client.post(
            reverse("register"),
            {"mac_address": mac_address},
        )

        self.assertEqual(response.status_code, 201)

        users = models.User.objects.all()
        self.assertEqual(len(users), 1)

        user = users[0]
        hashed_mac = get_hashed_mac(self.device_1_mac)
        self.assertEqual(user.mac_address, hashed_mac)

    def test_register_multiple(self):
        response_1 = self.client.post(
            reverse("register"),
            {"mac_address": self.device_1_mac},
        )
        response_2 = self.client.post(
            reverse("register"),
            {"mac_address": self.device_2_mac},
        )
        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_2.status_code, 201)

        users = models.User.objects.all()
        self.assertEqual(len(users), 2)

        user_1 = users[0]
        user_1_hashed_mac = get_hashed_mac(self.device_1_mac)
        user_2 = users[1]
        user_2_hashed_mac = get_hashed_mac(self.device_2_mac)

        self.assertEqual(user_1.mac_address, user_1_hashed_mac)
        self.assertEqual(user_2.mac_address, user_2_hashed_mac)
