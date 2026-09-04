from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="wallet", on_delete=models.CASCADE
    )
    balance = models.PositiveBigIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.balance})"
