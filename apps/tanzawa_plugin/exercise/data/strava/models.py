import datetime

from django.contrib.auth import models as auth_models
from django.db import models
from django.utils import timezone


class Athlete(models.Model):
    user = models.OneToOneField(auth_models.User, on_delete=models.CASCADE)
    athlete_id = models.BigIntegerField(unique=True)

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AccessToken(models.Model):
    athlete = models.OneToOneField(Athlete, on_delete=models.CASCADE, related_name="access_token")

    expires_at = models.DateTimeField()
    token = models.CharField(max_length=128)

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def update(self, token: str, expires_at: datetime.datetime) -> None:
        self.token = token
        self.expires_at = expires_at
        self.save()


class RefreshToken(models.Model):
    athlete = models.OneToOneField(Athlete, on_delete=models.CASCADE, related_name="refresh_token")

    token = models.CharField(max_length=128)

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update(self, token: str) -> None:
        self.token = token
        self.save()
