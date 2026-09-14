from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from .forms import WalletTopUpForm
from .models import Transaction, Wallet
from .services import WalletService

User = get_user_model()


class WalletDetailView(LoginRequiredMixin, DetailView):
    model = Wallet
    template_name = "pages/detail.html"
    context_object_name = "wallet"

    def get_object(self, queryset=None):
        return self.request.user.wallet  # pyright: ignore[reportAttributeAccessIssue]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        wallet = self.object
        context.update(
            {
                "page_title": "My Wallet",
                "nav_active": "billing",
                "eyebrow": "Wallet",
                "page_description": "Your current balance.",
                "fields": [
                    {"label": "Balance", "value": f"{wallet.balance:,} Toman"},
                ],
                "back_url": reverse_lazy("dashboard"),
                "primary_action": {
                    "label": "Top up",
                    "url": reverse_lazy("wallet:top-up"),
                    "icon": "plus",
                },
            }
        )
        return context


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "pages/list.html"
    context_object_name = "transaction"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Transaction]:
        return Transaction.objects.filter(wallet__account=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Transaction History",
                "nav_active": "billing",
                "eyebrow": "Wallet",
                "page_description": "All deposits and payments on your account.",
                "columns": [
                    {"label": "Type", "key": "type"},
                    {"label": "Amount", "key": "amount"},
                    {"label": "Date", "key": "created_at"},
                ],
                "empty_title": "No transactions yet",
                "empty_description": "Top up your wallet to see activity here.",
            }
        )
        return context


class WalletTopUpView(LoginRequiredMixin, FormView):
    template_name = "pages/wallet_top_up.html"
    form_class = WalletTopUpForm
    success_url = reverse_lazy("wallet:top-up")

    @staticmethod
    def get_or_create_wallet(*, account: User) -> Wallet:
        wallet, _ = Wallet.objects.get_or_create(account=account)
        return wallet

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        wallet = self.get_or_create_wallet(account=self.request.user)  # pyright: ignore[reportArgumentType]
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Top up wallet",
                "nav_active": "billing",
                "eyebrow": "Wallet",
                "page_description": "Add money to your wallet for appointment payments.",
                "wallet": wallet,
                "recent_transactions": list(wallet.transactions.order_by("-created_at")[:5]),  # pyright: ignore[reportAttributeAccessIssue]
                "preset_amounts": [10_000, 20_000, 50_000, 100_000],
                "submit_url": reverse_lazy("wallet:top-up"),
            }
        )
        return context

    def form_valid(self, form) -> Any:
        wallet = self.get_or_create_wallet(account=self.request.user)  # pyright: ignore[reportArgumentType]
        amount = form.cleaned_data["amount"]

        try:
            WalletService.top_up_wallet(account=self.request.user, amount=amount)  # pyright: ignore[reportArgumentType]
        except Exception as exc:
            form.add_error("amount", str(exc))
            return self.form_invalid(form)

        wallet.refresh_from_db()
        messages.success(self.request, f"{amount:,} Toman added to your wallet.")
        return super().form_valid(form)
