import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.generic import CreateView

from .forms import RegisterForm
from .models import OTP
from .services import OTPRateLimitError, OTPService, OTPServiceError

logger = logging.getLogger(__name__)


User = get_user_model()


class RegisterView(UserPassesTestMixin, CreateView):
    model = User
    form_class = RegisterForm
    template_name = "account/signup.html"

    def test_func(self) -> bool | None:
        return not self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect("")  # TODO: redirect the user to the home page

    def form_valid(self, form: RegisterForm) -> HttpResponse:
        self.request.session.update({"signup_data": form.cleaned_data})
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
            messages.error(self.request, _("We could not send a verification code right now. Please try again."))
            return self.form_invalid(form)

        messages.success(
            self.request,
            _("We sent a verification code to your phone number. If you didn't receive any message, check your email."),
        )
        return redirect("accounts:register")  # TODO: redirect to the verify otp page
