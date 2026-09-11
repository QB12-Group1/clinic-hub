import logging
from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _lazy
from django.views.generic import FormView, View

from patients.models import Patient

from .forms import LoginForm, RegisterForm, VerifyOTPForm
from .models import OTP
from .services import OTPRateLimitError, OTPService, OTPServiceError

logger = logging.getLogger(__name__)


User = get_user_model()


class RegisterView(UserPassesTestMixin, FormView):
    model = User
    form_class = RegisterForm
    template_name = "account/signup.html"

    def test_func(self) -> bool | None:
        return not self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect("")  # TODO: redirect the user to the home page

    def form_valid(self, form: RegisterForm) -> HttpResponse:
        self.request.session["auth_data"] = {"credentials": {**form.cleaned_data}, "purpose": OTP.Purpose.SIGNUP}
        if not self.request.session.session_key:
            self.request.session.create()

        purpose = OTP.Purpose.SIGNUP
        email = form.cleaned_data["email"]
        phone_number = form.cleaned_data["phone_number"]

        try:
            OTPService.send_sms_with_fallback(email=email, phone_number=phone_number, purpose=purpose)
        except OTPRateLimitError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except OTPServiceError:
            logger.exception("Failed to send signup OTP")
            messages.error(self.request, _lazy("We could not send a verification code right now. Please try again."))
            return self.form_invalid(form)

        messages.success(
            self.request,
            _lazy(
                "We sent a verification code to your phone number. If you didn't receive any message, check your email."
            ),
        )
        return redirect("accounts:verify_otp")


class LoginView(UserPassesTestMixin, FormView):
    form_class = LoginForm
    template_name = "account/login.html"

    def test_func(self) -> bool | None:
        return not self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect("")  # TODO: redirect user to the home page

    def form_valid(self, form: LoginForm) -> HttpResponse:
        credential = form.cleaned_data["credential"]
        account = User.objects.filter(Q(email=credential) | Q(phone_number=credential)).first()
        if not account:
            form.add_error("credential", _lazy("No account found with these credentials."))
            return self.form_invalid(form)

        auth_data = {
            "credentials": {
                "email": account.email,  # pyright: ignore[reportAttributeAccessIssue]
                "phone_number": account.phone_number,  # pyright: ignore[reportAttributeAccessIssue]
            },
            "purpose": OTP.Purpose.LOGIN,
        }
        self.request.session["auth_data"] = auth_data

        try:
            OTPService.send_sms_with_fallback(**auth_data["credentials"], purpose=auth_data["purpose"])
        except OTPRateLimitError as e:
            messages.error(self.request, str(e))
        except OTPServiceError:
            logger.exception("Failed to send signup OTP")
            messages.error(self.request, _lazy("We could not send a verification code right now. Please try again."))

        return redirect("accounts:verify_otp")


class RequestOTPView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        auth_data = request.session["auth_data"]
        credentials = auth_data["credentials"]
        purpose = auth_data["purpose"]
        try:
            OTPService.send_sms_with_fallback(**credentials, purpose=purpose)
        except OTPRateLimitError as e:
            messages.error(self.request, str(e))
        except OTPServiceError:
            logger.exception("Failed to send signup OTP")
            messages.error(self.request, _lazy("We could not send a verification code right now. Please try again."))
        return redirect("accounts:verify_otp")


class VerifyOTPView(FormView):
    form_class = VerifyOTPForm
    template_name = "account/verify_otp.html"

    def form_valid(self, form: VerifyOTPForm) -> HttpResponse:
        auth_data = self.request.session.get("auth_data")
        if not auth_data:
            messages.error(self.request, _lazy("We couldn't complete your request. Please try again."))
            return redirect("account:request_otp")

        credentials = auth_data["credentials"]
        purpose, raw_code = auth_data["purpose"], form.cleaned_data["code"]
        is_verified, message = OTPService.verify(**credentials, purpose=purpose, raw_code=raw_code)
        if not is_verified and message:
            form.add_error("code", message)
            return self.form_invalid(form)
        else:
            account, _ = User.objects.get_or_create(**credentials)
            patient_profile, _ = Patient.objects.get_or_create(account=account)
            if not self.request.user.is_authenticated:
                user = authenticate(self.request, **credentials)
                if user:
                    login(self.request, user)

        del auth_data
        return redirect("")  # TODO: redirect the user to the home page

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        credentials = self.request.session["auth_data"]["credentials"]
        purpose = self.request.session["auth_data"]["purpose"]
        context = super().get_context_data(**kwargs)
        context["wrong_credentials_url"] = (
            reverse_lazy("accounts:register") if purpose == OTP.Purpose.SIGNUP else reverse_lazy("accounts:login")
        )
        context["auth_phone_number"] = credentials["phone_number"]
        return context
