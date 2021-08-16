from django.db import models
import secrets

# Create your models here.


class AccessTokens(models.Model):
    """Access tokens."""

    service = models.CharField(max_length=60, unique=True, null=False)
    token = models.CharField(max_length=255, unique=True, null=False)
    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Create a unique token and save."""
        self.token = secrets.token_hex(24)
        super().save(*args, **kwargs)


class User(models.Model):
    mac_address = models.CharField(max_length=255, unique=False, null=False)
    mac_address_unhashed = models.CharField(max_length=255, unique=False, null=False)
    user_pin = models.CharField(max_length=255, unique=True, null=False)
