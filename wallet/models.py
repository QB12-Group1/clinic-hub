from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Wallet(models.Model):
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="wallet",
        on_delete=models.CASCADE,
    )
    balance = models.PositiveBigIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.account.username} ({self.balance})"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", _("Deposit")
        WITHDRAWAL = "withdrawal", _("Withdrawal")
        PAYMENT = "payment", _("Payment")

    wallet = models.ForeignKey(
        Wallet,
        related_name="transactions",
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        max_length=15,
        choices=TransactionType.choices,
    )
    amount = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.wallet} - {self.type} - {self.amount}"
