# Generated by Django 2.2.13 on 2020-11-19 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("security_manager", "0003_auto_20201111_2052"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="hashed_mac",
            new_name="mac_address",
        ),
        migrations.RenameField(
            model_name="user",
            old_name="username",
            new_name="user_pin",
        ),
        migrations.RemoveField(
            model_name="user",
            name="admin",
        ),
        migrations.RemoveField(
            model_name="user",
            name="password_hash",
        ),
    ]
