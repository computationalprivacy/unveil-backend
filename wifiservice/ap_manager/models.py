"""Models for InternetAnalysis"""
import uuid
import binascii

from constants import (
    DEVICE_INFO,
    MAC_ADDRESS,
    MANUFACTURER,
    MODEL_NUMBER,
    USER_AGENT,
    OS_VERSION,
    USER_PIN,
    DNS_QUERIES,
    INTERNET_TRAFFIC,
    FILTERS,
    LAST_UPDATED,
    RATING,
    HTTP,
    HTTPS,
    SENSITIVE,
    NOT_SENSITIVE,
    DEVICE_ID,
    DEVICE_PIN,
    SHOW_DEVICE_INFO,
    SHOW_DNS_QUERIES,
    SHOW_SECURE_INTERNET_TRAFFIC,
    SHOW_UNSECURE_INTERNET_TRAFFIC,
    DIFFERENTIATE_TRACKERS,
    SHOW_DEVICE,
    DEVICE_POSITION, NOT_AVAILABLE,
)
from django.db import models
from django.db.models import CASCADE


class Connection(models.Model):
    """A record of an internet connection from a device."""

    objects: models.Manager()
    time = models.DateTimeField(auto_now=True, null=False)
    destination = models.URLField(null=False)
    type = models.CharField(max_length=5, choices=[(HTTP, "HTTP"), (HTTPS, "HTTPS")])
    size = models.CharField(max_length=20, null=False)
    is_tracker = models.BooleanField(null=False)

    def to_json(self):
        return [
            str(self.time.strftime("%H:%M:%S")),
            self.destination,
            self.type,
            self.size,
            self.is_tracker,
        ]

    class Meta:
        ordering = ['-time']


class DNSQuery(models.Model):
    """A record of a dns query from a device."""

    url = models.URLField(null=False)
    type = models.CharField(
        max_length=15,
        choices=[(SENSITIVE, "SENSITIVE"), (NOT_SENSITIVE, "NOT SENSITIVE")],
        null=False,
    )

    def to_json(self):
        return [self.url, str(self.type).lower()]


class Filters(models.Model):
    """Display filters associated with a device."""

    device_id = models.CharField(max_length=255)
    show_device_info = models.BooleanField(default=False)
    show_dns_queries = models.BooleanField(default=False)
    show_secure_internet_traffic = models.BooleanField(default=False)
    show_unsecure_internet_traffic = models.BooleanField(default=False)
    differentiate_trackers = models.BooleanField(default=False)
    show_device = models.BooleanField(default=False)
    device_position = models.IntegerField(default=-1)
    device_pin = models.CharField(max_length=255)

    def to_json(self):
        return {
            DEVICE_ID: self.device_id,
            DEVICE_PIN: self.device_pin,
            SHOW_DEVICE_INFO: self.show_device_info,
            SHOW_DNS_QUERIES: self.show_dns_queries,
            SHOW_SECURE_INTERNET_TRAFFIC: self.show_secure_internet_traffic,
            SHOW_UNSECURE_INTERNET_TRAFFIC: self.show_unsecure_internet_traffic,
            DIFFERENTIATE_TRACKERS: self.differentiate_trackers,
            SHOW_DEVICE: self.show_device,
            DEVICE_POSITION: self.device_position,
        }

    def to_json_with_rating(self):
        json = self.to_json()
        json[RATING] = Device.objects.get(display_filters__pk=self.pk).rating

        return json

    def update_filters(self, updated_filter):
        if self.device_id != updated_filter.get(DEVICE_ID):
            return

        self.show_device_info = updated_filter.get(
            SHOW_DEVICE_INFO, self.show_device_info
        )
        self.show_dns_queries = updated_filter.get(
            SHOW_DNS_QUERIES, self.show_dns_queries
        )
        self.show_secure_internet_traffic = updated_filter.get(
            SHOW_SECURE_INTERNET_TRAFFIC, self.show_secure_internet_traffic
        )
        self.show_unsecure_internet_traffic = updated_filter.get(
            SHOW_UNSECURE_INTERNET_TRAFFIC, self.show_unsecure_internet_traffic
        )
        self.differentiate_trackers = updated_filter.get(
            DIFFERENTIATE_TRACKERS, self.differentiate_trackers
        )
        self.show_device = updated_filter.get(SHOW_DEVICE, self.show_device)
        self.device_position = updated_filter.get(DEVICE_POSITION, self.device_position)

        self.save()


class Session(models.Model):
    """A demonstration session."""

    session_id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    creation_time = models.DateTimeField(auto_now_add=True)


class Screenshot(models.Model):
    """A record of a screenshot."""

    session_id = models.ForeignKey(to=Session, on_delete=CASCADE)
    url = models.URLField(null=False, unique=True)
    image = models.BinaryField(null=True)

    def to_json(self):
        if self.image:
            return [
                binascii.b2a_base64(self.image.tobytes(), newline=False).decode(
                    "ascii"
                ),
                self.url,
            ]


class Device(models.Model):
    """A record of a device."""

    mac = models.CharField(max_length=255, null=False)
    manufacturer = models.CharField(max_length=255, default=NOT_AVAILABLE, null=False)
    model_number = models.CharField(max_length=255, default=NOT_AVAILABLE, null=False)
    user_agent = models.CharField(max_length=255, default=NOT_AVAILABLE, null=False)
    os_version = models.CharField(max_length=255, default=NOT_AVAILABLE, null=False)

    traffic = models.ManyToManyField(Connection, null=True)
    dns_queries = models.ManyToManyField(DNSQuery, null=True)

    pin = models.CharField(max_length=10)
    display_filters = models.ForeignKey(to=Filters, on_delete=CASCADE, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    rating = models.FloatField(default=0.0)
    session_id = models.ForeignKey(to=Session, on_delete=CASCADE)

    class Meta:
        unique_together = ["mac", "session_id"]
        ordering = ['pk']

    def to_json(self):
        return {
            DEVICE_INFO: {
                MAC_ADDRESS: self.mac,
                MANUFACTURER: self.manufacturer,
                MODEL_NUMBER: self.model_number,
                USER_AGENT: self.user_agent,
                OS_VERSION: self.os_version,
            },
            USER_PIN: self.pin,
            DNS_QUERIES: [dns_query.to_json() for dns_query in self.dns_queries.all()],
            INTERNET_TRAFFIC: [
                connection.to_json() for connection in self.traffic.all()
            ],
            FILTERS: self.display_filters.to_json(),
            LAST_UPDATED: self.last_updated,
            RATING: self.rating,
        }
