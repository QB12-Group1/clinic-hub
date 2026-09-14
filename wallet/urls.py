from django.urls import path

from wallet import views

app_name = "wallet"

urlpatterns = [
    path("", views.WalletDetailView.as_view(), name="detail"),
    path("top-up/", views.WalletTopUpView.as_view(), name="top-up"),
    path(
        "appointments/<int:pk>/pay-with-wallet/", views.WalletAppointmentPaymentView.as_view(), name="pay-appointment"
    ),
    path("transaction/", views.TransactionListView.as_view(), name="transaction-list"),
]
