from django.urls import path

from wallet import views

app_name = "wallet"

urlpatterns = [
    path("", views.WalletDetailView.as_view(), name="detail"),
]
