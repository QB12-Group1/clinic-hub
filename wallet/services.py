from django.contrib.auth import get_user_model
from django.db import transaction
from wallet.models import Transaction, Wallet

User = get_user_model()


class InsufficientBalanceError(Exception):
    """Raised when a wallet has insufficient balance."""


class WalletService:
    def _validate_amount(self, amount: int) -> None:

        if amount <= 0:
            raise ValueError("amount must be greater than 0")

    def top_up_wallet(self, *, account: User, amount: int) -> Wallet:

        self._validate_amount(amount)

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(account=account)
            wallet.balance += amount
            wallet.save(update_fields=["balance"])

            Transaction.objects.create(
                wallet=wallet,
                type=Transaction.TransactionType.DEPOSIT,
                amount=amount,
            )
            return wallet

    def debit_wallet(self, *, account: User, amount: int) -> Wallet:

        self._validate_amount(amount)

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(account=account)

            if wallet.balance < amount:
                raise InsufficientBalanceError(
                    f"Wallet balance ({wallet.balance}) is less than the required amount ({amount})."
                )

            wallet.balance -= amount
            wallet.save(update_fields=["balance"])

            Transaction.objects.create(
                wallet=wallet,
                type=Transaction.TransactionType.PAYMENT,
                amount=amount,
            )
            return wallet
