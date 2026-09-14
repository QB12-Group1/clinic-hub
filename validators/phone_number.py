from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class PhoneNumberValidator(RegexValidator):
    regex = r"^09[0-9]{9}$"
    message = _("Phone number must be in the format '09123456789' (11 digits).")
    code = "invalid_phone_number"
