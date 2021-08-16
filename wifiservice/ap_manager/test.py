"""Tests for ap_manager endpoints"""
import uuid
from pathlib import Path
from unittest.mock import patch

from django.test import Client, TestCase

from ap_manager import models
from ap_manager.analysis import analyze_helper
from ap_manager.analyzer.analyzer import NOT_AVAILABLE
from security_manager.utils import register_user

FIXTURES_FOLDER = Path(__file__).parent.absolute() / "fixtures"


@patch("ap_manager.analysis.os")  # Patch os to avoid deleting data file
@patch("ap_manager.analysis.generate_new_screenshots")  # Avoid creating screenshots
class AccessPointManagerTests(
    TestCase
):  # Intended to use LiveServerTestCase here but had some issues making POST req
    def setUp(self) -> None:
        self.client = Client()
        self.session = models.Session.objects.create()

        self.device_1_mac = "04:d6:aa:15:b8:b0"
        self.device_1_hashed_mac = "0547d436d2a8e12e449e0645d2f7b8d8"

        self.device_2_mac = "fe:40:d9:b4:fd:d2"
        self.device_2_hashed_mac = "dfe92d902f4113044e8ca0c8eb91c0c1"

        self.device_3_mac = "ba:67:e4:2d:27:ab"
        self.device_3_hashed_mac = "2a664cc05626fe04a101b0c337d81648"

    def _analyze_fixture(self, relative_path):
        fixture = open(str(FIXTURES_FOLDER / f"{relative_path}.pcapng"), "rb")
        analyze_helper(self.session.session_id, fixture)

    def test_analyze_non_existing_session(self, mock_os, mock_screenshot):
        with self.assertRaises(ValueError):
            fixture = open(str(FIXTURES_FOLDER / "data1.pcapng"), "rb")
            analyze_helper(uuid.uuid4(), fixture)

    def test_analyze_users_not_consented(self, mock_os, mock_screenshot):
        self._analyze_fixture("data1")

        self.assertEqual(models.Device.objects.count(), 0)
        self.assertEqual(models.Connection.objects.count(), 0)
        self.assertEqual(models.DNSQuery.objects.count(), 0)
        self.assertEqual(models.Filters.objects.count(), 0)

    def test_analyze_user_consented_device_info(self, mock_os, mock_screenshot):
        expected_mac = "2a664cc05626fe04a101b0c337d81648"
        expected_manufacturer = NOT_AVAILABLE
        expected_model_number = "ONEPLUS A6013"
        expected_user_agent = "Mozilla/5.0 (Linux; Android 10; ONEPLUS A6013 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.198 Mobile Safari/537.36"
        expected_os_version = "Android "

        register_user(self.device_3_mac)
        self._analyze_fixture("data1")

        devices = models.Device.objects.all()
        self.assertEqual(len(devices), 1)

        device = devices[0]
        self.assertEqual(device.mac, expected_mac)
        self.assertEqual(device.manufacturer, expected_manufacturer)
        self.assertEqual(device.model_number, expected_model_number)
        self.assertEqual(device.user_agent, expected_user_agent)
        self.assertEqual(device.os_version, expected_os_version)

    def test_analyze_user_consented_traffic(self, mock_os, mock_screenshot):
        expected_traffic_destinations = [
            "gcp.api.snapchat.com",
            "edge-mqtt.facebook.com",
        ]

        register_user(self.device_1_mac)
        self._analyze_fixture("data2")
        devices = models.Device.objects.all()

        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].mac, self.device_1_hashed_mac)

        device = devices[0]
        actual_traffic_destinations = device.traffic.all().values_list(
            "destination", flat=True
        )

        self.assertEqual(
            set(actual_traffic_destinations), set(expected_traffic_destinations)
        )

    def test_analyze_user_consented_dns_queries(self, mock_os, mock_screenshot):
        expected_dns_urls = [
            "firebase-settings.crashlytics.com",
            "api2.branch.io",
            "gcp.api.snapchat.com",
            "b-graph.facebook.com",
            "graph.facebook.com",
            "edge-mqtt.facebook.com",
            "firebaseinstallations.googleapis.com",
        ]

        register_user(self.device_1_mac)
        self._analyze_fixture("data2")
        devices = models.Device.objects.all()

        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].mac, self.device_1_hashed_mac)

        device = devices[0]
        actual_dns_urls = device.dns_queries.all().values_list("url", flat=True)

        self.assertEqual(set(actual_dns_urls), set(expected_dns_urls))
