# Generated by Django 2.2.13 on 2020-11-20 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("security_manager", "0004_auto_20201119_2022"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="mac_address_unhashed",
            field=models.CharField(default="ee:53:c4:37:a5:84", max_length=255),
            preserve_default=False,
        ),
    ]