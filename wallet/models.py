from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.PositiveBigIntegerField()

    def __str__(self) -> str:
        return f"{self.user.username} ({self.balance})"
