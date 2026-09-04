from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.http.request import HttpRequest
from django.views.decorators.debug import sensitive_variables

import utils

User = get_user_model()


# WARNING: Dear developer :), do not use this without confirming credentials.
# Make sure to use the OTP service to validate the user's identity, then authenticate.
# (This is actually a note to my idiot self, not you, my beloved teammates)
class PhoneBackend(BaseBackend):
    @sensitive_variables("otp")
    def authenticate(
        self,
        request: HttpRequest | None,
        phone_number: str | None = None,
        **kwargs: Any,
    ) -> User | None:
        if not phone_number:
            return None

        phone_number = utils.normalize_phone_number(phone_number)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return None

        if not self.user_can_authenticate(user):
            return None

        return user

    def user_can_authenticate(self, user: User) -> bool:
        return getattr(user, "is_active", True)

    def get_user(self, user_id: int) -> User | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
