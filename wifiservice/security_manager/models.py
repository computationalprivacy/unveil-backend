from django.db import models
import secrets

# Create your models here.


class AccessTokens(models.Model):
    """Access tokens."""
    service = models.CharField(max_length=60, unique=True, null=False)
    token = models.CharField(max_length=24, unique=True, null=False)
    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Create a unique token and save."""
        self.token = secrets.token_hex(24)
        super().save(*args, **kwargs)
