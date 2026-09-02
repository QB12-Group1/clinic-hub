from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.PositiveBigIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.balance})"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT = "credit", _("Credit")
        DEBIT = "debit", _("Debit")

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.wallet} - {self.type} - {self.amount}"
