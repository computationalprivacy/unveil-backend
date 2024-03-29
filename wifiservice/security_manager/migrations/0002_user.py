# Generated by Django 2.2.13 on 2020-11-11 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("security_manager", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("hashed_mac", models.CharField(max_length=255)),
                ("username", models.CharField(max_length=255, unique=True)),
                ("password_hash", models.CharField(max_length=255)),
                ("admin", models.BooleanField(default=False)),
            ],
        ),
    ]
