from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView

from wallet.models import Transaction, Wallet


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
                "nav_active": "wallet",
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
    paginate_by = 20

    def get_queryset(self) -> QuerySet[Transaction]:
        return Transaction.objects.filter(wallet__account=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Transaction History",
                "nav_active": "wallet",
                "eyebrow": "Wallet",
                "page_description": "All deposits and payments on your account.",
                "columns": [
                    {"label": "Type", "key": "get_type_display"},
                    {"label": "Amount", "key": "amount"},
                    {"label": "Date", "key": "created_at"},
                ],
                "empty_title": "No transactions yet",
                "empty_description": "Top up your wallet to see activity here.",
            }
        )
        return context
