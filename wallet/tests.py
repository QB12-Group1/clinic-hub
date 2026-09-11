from django.test import TestCase

from accounts.models import User
from wallet.models import Transaction as WalletTransaction
from wallet.models import Wallet
from django.db import IntegrityError, transaction


class WalletModelTests(TestCase):
    def setUp(self):
        self.account = User.objects.create_user(phone_number="09123456789", email="test@example.com", first_name="Ali")  # pyright: ignore[reportCallIssue]

    def test_wallet_default_balance_is_zero(self):
        wallet = Wallet.objects.create(account=self.account)
        self.assertIsNotNone(wallet.pk)
        self.assertEqual(wallet.account, self.account)
        self.assertEqual(wallet.balance, 0)

    def test_one_account_cannot_have_two_wallets(self):
        Wallet.objects.create(account=self.account)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Wallet.objects.create(account=self.account)


class TransactionModelTests(TestCase):
    def setUp(self):
        account = User.objects.create_user(phone_number="09123456789", email="test@example.com" ,first_name="Ali")  # pyright: ignore[reportCallIssue]
        self.wallet = Wallet.objects.create(account=account)

    def test_transaction_creation_and_related_name(self):
        WalletTransaction.objects.create(
            wallet=self.wallet, type=WalletTransaction.TransactionType.DEPOSIT, amount=100000
        )
        self.assertEqual(self.wallet.transactions.count(), 1)  # pyright: ignore[reportAttributeAccessIssue]
