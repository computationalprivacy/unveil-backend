"""Unit tests for filters"""

from django.test import LiveServerTestCase, Client
from django.urls import reverse

from ap_manager import models
from constants import (
    DEVICE_ID,
    DEVICE_PIN,
    SHOW_DEVICE_INFO,
    SHOW_DNS_QUERIES,
    SHOW_SECURE_INTERNET_TRAFFIC,
    SHOW_UNSECURE_INTERNET_TRAFFIC,
    DIFFERENTIATE_TRACKERS,
    RATING,
    SHOW_DEVICE,
    DEVICE_POSITION,
)


class FilterTests(LiveServerTestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.session = models.Session.objects.create()
        self.device_1_hashed_mac = "0547d436d2a8e12e449e0645d2f7b8d8"
        self.device_2_hashed_mac = "dfe92d902f4113044e8ca0c8eb91c0c1"

    def test_get_filters_no_associated_device(self):
        models.Filters.objects.create(device_id=self.device_1_hashed_mac)

        response = self.client.get(
            reverse("get-filters", kwargs={"session_id": self.session.session_id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"filters": []})

    def test_get_filters_no_associated_session(self):
        session = models.Session.objects.create()
        filters = models.Filters.objects.create(device_id=self.device_1_hashed_mac)
        models.Device.objects.create(
            mac=self.device_1_hashed_mac, display_filters=filters, session_id=session
        )

        response = self.client.get(
            reverse("get-filters", kwargs={"session_id": self.session.session_id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"filters": []})

    def test_get_filters(self):
        filters = models.Filters.objects.create(device_id=self.device_1_hashed_mac)
        models.Device.objects.create(
            mac=self.device_1_hashed_mac,
            display_filters=filters,
            session_id=self.session,
        )

        response = self.client.get(
            reverse("get-filters", kwargs={"session_id": self.session.session_id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "filters": [
                    {
                        DEVICE_ID: self.device_1_hashed_mac,
                        DEVICE_PIN: "",
                        SHOW_DEVICE_INFO: False,
                        SHOW_DNS_QUERIES: False,
                        SHOW_SECURE_INTERNET_TRAFFIC: False,
                        SHOW_UNSECURE_INTERNET_TRAFFIC: False,
                        DIFFERENTIATE_TRACKERS: False,
                        RATING: 0.0,
                        SHOW_DEVICE: False,
                        DEVICE_POSITION: -1,
                    }
                ]
            },
        )

    def test_set_filters(self):
        filters = models.Filters.objects.create(device_id=self.device_1_hashed_mac)
        models.Device.objects.create(
            mac=self.device_1_hashed_mac,
            display_filters=filters,
            session_id=self.session,
        )

        response = self.client.post(
            reverse("set-filters", kwargs={"session_id": self.session.session_id}),
            data=[
                {
                    DEVICE_ID: self.device_1_hashed_mac,
                    DEVICE_PIN: "1234",
                    SHOW_DEVICE_INFO: True,
                    SHOW_DNS_QUERIES: False,
                    SHOW_SECURE_INTERNET_TRAFFIC: True,
                    SHOW_UNSECURE_INTERNET_TRAFFIC: False,
                    DIFFERENTIATE_TRACKERS: True,
                    SHOW_DEVICE: False,
                    DEVICE_POSITION: 42,
                },
            ],
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        display_filters = models.Filters.objects.all()
        self.assertEqual(len(display_filters), 1)

        display_filter = display_filters[0]
        self.assertEqual(
            display_filter.to_json(),
            {
                DEVICE_ID: self.device_1_hashed_mac,
                DEVICE_PIN: "",
                SHOW_DEVICE_INFO: True,
                SHOW_DNS_QUERIES: False,
                SHOW_SECURE_INTERNET_TRAFFIC: True,
                SHOW_UNSECURE_INTERNET_TRAFFIC: False,
                DIFFERENTIATE_TRACKERS: True,
                SHOW_DEVICE: False,
                DEVICE_POSITION: 42,
            },
        )
