from django.test import TestCase

from accounts.models import User
from wallet.models import Transaction as WalletTransaction
from wallet.models import Wallet
from wallet.services import InsufficientBalanceError, WalletService


class ToUpWalletServiceTests(TestCase):
    def setUp(self) -> None:
        self.account = User.objects.create_user(phone_number="09123456789", email="test@example.com", first_name="Ali")  # pyright: ignore[reportCallIssue]
        self.wallet = Wallet.objects.create(account=self.account)

    def test_top_up_increases_balance(self) -> None:
        WalletService.top_up_wallet(account=self.account, amount=500000)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 500000)

    def test_top_up_creates_deposit_transaction(self) -> None:
        WalletService.top_up_wallet(account=self.account, amount=500000)
        record = self.wallet.transactions.get()  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(record.type, WalletTransaction.TransactionType.DEPOSIT)

    def test_top_up_rejects_zero_or_negative_amount(self) -> None:
        with self.assertRaises(ValueError):
            WalletService.top_up_wallet(account=self.account, amount=0)
        with self.assertRaises(ValueError):
            WalletService.top_up_wallet(account=self.account, amount=-10000)


class DebitWalletServiceTests(TestCase):
    def setUp(self) -> None:
        self.account = User.objects.create_user(phone_number="09123456789", email="test@example.com", first_name="Ali")  # pyright: ignore[reportCallIssue]
        self.wallet = Wallet.objects.create(account=self.account, balance=100000)

    def test_charge_decreases_balance(self) -> None:
        WalletService.charge_wallet(account=self.account, amount=40000)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 60000)

    def test_charge_creates_payment_transaction(self) -> None:
        WalletService.charge_wallet(account=self.account, amount=50000)
        record = self.wallet.transactions.get()  # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(record.type, WalletTransaction.TransactionType.PAYMENT)

    def test_charge_rejects_when_balance_insufficient(self) -> None:
        with self.assertRaises(InsufficientBalanceError):
            WalletService.charge_wallet(account=self.account, amount=99999999)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 100000)
