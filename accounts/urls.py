from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("request-otp/", views.RequestOTPView.as_view(), name="request_otp"),
]
