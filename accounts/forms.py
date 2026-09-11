from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.forms.models import ModelForm
from django.utils.translation import gettext_lazy as _

from accounts.services import OTPService

User = get_user_model()


class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "email")


class VerifyOTPForm(forms.Form):
    code = forms.CharField(
        min_length=OTPService.CODE_LENGTH,
        max_length=OTPService.CODE_LENGTH,
        required=True,
        help_text=_("The code sent to you by SMS. (Note: If you didn't receive it, check your email.)"),
        validators=[RegexValidator(rf"^[{OTPService.ALLOWED_CHARS}]+$")],
    )
