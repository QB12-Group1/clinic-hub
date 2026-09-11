from django.contrib.auth import get_user_model
from django.db import transaction
from wallet.models import Transaction, Wallet

User = get_user_model()


class InsufficientBalanceError(Exception):
    """Raised when a wallet's balance is too low to cover a requested charge."""


def _validate_amount(amount: int) -> None:

    if not isinstance(amount, int) or isinstance(amount, bool):
        raise TypeError(f"amount must be an int, got {type(amount).__name__}")


def top_up_wallet(*, account: User, amount: int) -> Wallet:

    _validate_amount(amount)

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


def charge_wallet(*, account: User, amount: int) -> Wallet:

    _validate_amount(amount)

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
