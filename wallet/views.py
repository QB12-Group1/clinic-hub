from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from wallet.models import Wallet


class WalletDetailView(LoginRequiredMixin, DetailView):
    model = Wallet
    template_name = "wallet/detail.html"
    context_object_name = "wallet"

    def get_object(self, queryset=None):
        return self.request.user.wallet  # pyright: ignore[reportAttributeAccessIssue]
