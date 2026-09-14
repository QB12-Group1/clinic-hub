import string
from datetime import timedelta

from django.contrib.auth.models import BaseUserManager
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

import utils
from accounts.models import OTP
from core.tasks import send_sms_task


class OTPServiceError(Exception):
    pass


class OTPRateLimitError(OTPServiceError):
    pass


class OTPService:
    CODE_LENGTH = 6
    EXPIRY_MINUTES = 2
    MAX_ATTEMPTS = 5
    COOLDOWN_SECONDS = 60
    ALLOWED_CHARS = string.digits

    @classmethod
    def _check_params(cls, kwargs: dict) -> dict[str, str]:
        purpose = kwargs.get("purpose")
        email = kwargs.get("email")
        phone_number = kwargs.get("phone_number")

        if not purpose:
            raise ValueError("Missing required parameter: 'purpose'.")

        if not email or not phone_number:
            raise ValueError("Both 'email' and 'phone_number' are required.")

        kwargs["email"] = BaseUserManager.normalize_email(email)
        kwargs["phone_number"] = utils.normalize_phone_number(phone_number)
        return kwargs

    @classmethod
    def _rate_limit_user(cls, **kwargs) -> None:
        is_allowed, remaining_seconds = cls.can_request_otp(**kwargs)
        if not is_allowed:
            raise OTPRateLimitError(f"Please wait {remaining_seconds} seconds before requesting a new code.")

    @classmethod
    def _apply_cooldown(cls, **kwargs) -> None:
        email, phone_number, purpose = kwargs.get("email"), kwargs.get("phone_number"), kwargs.get("purpose")
        cache_key = f"otp_cooldown:{email}:{phone_number}:{purpose}"
        cache.set(cache_key, True, timeout=cls.COOLDOWN_SECONDS)

    @classmethod
    def _create_otp_project(cls, **kwargs) -> tuple[str, OTP]:
        raw_code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=cls.EXPIRY_MINUTES)

        otp = OTP(
            email=kwargs.get("email"),
            phone_number=kwargs.get("phone_number"),
            purpose=kwargs.get("purpose"),
            max_attempts=cls.MAX_ATTEMPTS,
            expires_at=expires_at,
        )
        otp.set_code(raw_code)
        otp.save()
        return raw_code, otp

    @classmethod
    def generate_code(cls) -> str:
        return get_random_string(cls.CODE_LENGTH, cls.ALLOWED_CHARS)

    @classmethod
    def can_request_otp(cls, **kwargs) -> tuple[bool, int]:
        kwargs = cls._check_params(kwargs)
        email, phone_number, purpose = kwargs.get("email"), kwargs.get("phone_number"), kwargs.get("purpose")
        cache_key = f"otp_cooldown:{email}:{phone_number}:{purpose}"
        remaining_ttl = cache.ttl(cache_key) if hasattr(cache, "ttl") else 0  # pyright: ignore[reportAttributeAccessIssue]
        if cache.get(cache_key):
            return False, remaining_ttl or cls.COOLDOWN_SECONDS
        return True, 0

    @classmethod
    def revoke_pending_otps(cls, **kwargs) -> int:
        kwargs = cls._check_params(kwargs)
        email = kwargs.get("email")
        phone_number = kwargs.get("phone_number")
        purpose = kwargs.get("purpose")
        now = timezone.now()
        return (
            OTP.objects.select_for_update()
            .filter(email=email, phone_number=phone_number, purpose=purpose, status=OTP.Status.PENDING)
            .update(status=OTP.Status.REVOKED, consumed_at=now)
        )

    @classmethod
    def send_sms_with_fallback(cls, **kwargs) -> OTP:
        kwargs = cls._check_params(kwargs)
        email = kwargs.get("email")
        phone_number = kwargs.get("phone_number")
        purpose = kwargs.get("purpose") or OTP.Purpose.LOGIN

        email = BaseUserManager.normalize_email(email)
        phone_number = utils.normalize_phone_number(phone_number)  # pyright: ignore[reportArgumentType]

        kwargs = {"email": email, "phone_number": phone_number, "purpose": purpose}
        cls._rate_limit_user(**kwargs)

        with transaction.atomic():
            cls.revoke_pending_otps(**kwargs)
            raw_code, otp = cls._create_otp_project(**kwargs)
            cls._apply_cooldown(**kwargs)

        PURPOSE_CONFIG = {
            "signup": {
                "subject": "Your Verification Code",
                "action_text": "verify your email address",
            },
            "login": {
                "subject": "Your Login OTP Code",
                "action_text": "log into your account",
            },
            "reset_password": {
                "subject": "Your Password Reset Code",
                "action_text": "reset your password",
            },
        }

        config = PURPOSE_CONFIG.get(purpose, {"subject": "Your Security Code", "action_text": "complete your request"})

        subject = config["subject"]
        message_text = (
            f"Your verification code to {config['action_text']} is: {raw_code}\n"
            f"This code is valid for {cls.EXPIRY_MINUTES} minutes.\n"
            "If you did not request this, please ignore this email."
        )

        transaction.on_commit(
            lambda: send_sms_task.delay(
                phone_number=phone_number,
                message_text=message_text,
                fallback_email=email,
                fallback_subject=subject,
                fallback_message_text=message_text,
            )
        )

        return otp

    @classmethod
    def verify(cls, **kwargs) -> tuple[bool, str | None]:
        kwargs = cls._check_params(kwargs)
        raw_code = kwargs.get("raw_code")
        if not raw_code:
            raise ValueError("Missing required parameter: 'raw_code'")

        with transaction.atomic():
            otp = (
                OTP.objects.select_for_update()
                .filter(
                    email=kwargs.get("email"),
                    phone_number=kwargs.get("phone_number"),
                    purpose=kwargs.get("purpose"),
                    status=OTP.Status.PENDING,
                )
                .order_by("-created_at", "-pk")
                .first()
            )

            if not otp:
                return False, _("No active OTP request found. Please request a new code.")

            if otp.is_expired:
                return False, _("Code has expired. Please request a new code.")

            if otp.is_exhausted:
                return False, _("Maximum attempts reached. Please request a new code.")

            if not otp.check_code(raw_code):
                otp.attempts_count += 1
                otp.save(update_fields=["attempts_count"])
                remaining_attempts = otp.max_attempts - otp.attempts_count
                return False, ngettext(
                    "Invalid code. %(count)d attempt remaining.",
                    "Invalid code. %(count)d attempts remaining.",
                    remaining_attempts,
                ) % {"count": remaining_attempts}

            otp.status = OTP.Status.VERIFIED
            otp.consumed_at = timezone.now()
            otp.save(update_fields=["status", "consumed_at"])
            return True, None
