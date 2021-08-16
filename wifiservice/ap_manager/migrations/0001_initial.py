# Generated by Django 2.2.13 on 2021-01-09 23:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Connection",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("time", models.DateTimeField(auto_now=True)),
                ("destination", models.URLField()),
                (
                    "type",
                    models.CharField(
                        choices=[("HTTP", "HTTP"), ("HTTPS", "HTTPS")], max_length=5
                    ),
                ),
                ("size", models.CharField(max_length=20)),
                ("is_tracker", models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name="DNSQuery",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.URLField()),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("SENSITIVE", "SENSITIVE"),
                            ("NOT SENSITIVE", "NOT SENSITIVE"),
                        ],
                        max_length=15,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Filters",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("device_id", models.CharField(max_length=255)),
                ("show_device_info", models.BooleanField(default=False)),
                ("show_dns_queries", models.BooleanField(default=False)),
                ("show_secure_internet_traffic", models.BooleanField(default=False)),
                ("show_unsecure_internet_traffic", models.BooleanField(default=False)),
                ("differentiate_trackers", models.BooleanField(default=False)),
                ("show_device", models.BooleanField(default=False)),
                ("device_position", models.IntegerField(default=-1)),
                ("device_pin", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Session",
            fields=[
                (
                    "session_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("creation_time", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Screenshot",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.URLField(unique=True)),
                ("image", models.BinaryField(null=True)),
                (
                    "session_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ap_manager.Session",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mac", models.CharField(max_length=255)),
                ("manufacturer", models.CharField(blank=True, max_length=255)),
                ("model_number", models.CharField(blank=True, max_length=255)),
                ("user_agent", models.CharField(blank=True, max_length=255)),
                ("os_version", models.CharField(blank=True, max_length=255)),
                ("pin", models.CharField(max_length=10)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("rating", models.FloatField()),
                (
                    "display_filters",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ap_manager.Filters",
                    ),
                ),
                (
                    "dns_queries",
                    models.ManyToManyField(null=True, to="ap_manager.DNSQuery"),
                ),
                (
                    "session_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ap_manager.Session",
                    ),
                ),
                (
                    "traffic",
                    models.ManyToManyField(null=True, to="ap_manager.Connection"),
                ),
            ],
            options={
                "unique_together": {("mac", "session_id")},
            },
        ),
    ]