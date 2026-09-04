import string
from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from accounts.models import OTP


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
    def generate_code(cls) -> str:
        return get_random_string(cls.CODE_LENGTH, cls.ALLOWED_CHARS)

    @classmethod
    def can_request_otp(cls, phone_number: str, purpose: str) -> tuple[bool, int]:
        cache_key = f"otp_cooldown:{phone_number}:{purpose}"
        remaining_ttl = cache.ttl(cache_key) if hasattr(cache, "ttl") else 0  # pyright: ignore[reportAttributeAccessIssue]
        if cache.get(cache_key):
            return False, remaining_ttl or cls.COOLDOWN_SECONDS
        return True, 0

    @classmethod
    def revoke_pending_otps(cls, phone_number: str, purpose: str) -> int:
        now = timezone.now()
        return (
            OTP.objects.select_for_update()
            .filter(
                phone_number=phone_number,
                purpose=purpose,
                status=OTP.Status.PENDING,
                expires_at__gt=now,
            )
            .update(status=OTP.Status.REVOKED, consumed_at=now)
        )

    @classmethod
    def send_sms(cls, phone_number: str, purpose: str) -> OTP:
        is_allowed, remaining_seconds = cls.can_request_otp(phone_number, purpose)
        if not is_allowed:
            raise OTPRateLimitError(
                f"Please wait {remaining_seconds} seconds before requesting a new code."
            )

        raw_code = cls.generate_code()
        print(raw_code)
        expires_at = timezone.now() + timedelta(minutes=cls.EXPIRY_MINUTES)

        with transaction.atomic():
            cls.revoke_pending_otps(phone_number, purpose)

            otp = OTP(
                phone_number=phone_number,
                purpose=purpose,
                max_attempts=cls.MAX_ATTEMPTS,
                expires_at=expires_at,
            )
            otp.set_code(raw_code)
            otp.save()

            cache_key = f"otp_cooldown:{phone_number}:{purpose}"
            cache.set(cache_key, True, timeout=cls.COOLDOWN_SECONDS)

        # TODO: actually send the raw code with sms
        return otp

    @classmethod
    def verify(
        cls, phone_number: str, purpose: str, raw_code: str
    ) -> tuple[bool, str | None]:
        with transaction.atomic():
            otp = (
                OTP.objects.select_for_update()
                .filter(
                    phone_number=phone_number,
                    purpose=purpose,
                    status=OTP.Status.PENDING,
                )
                .order_by("-created_at", "-pk")
                .first()
            )

            if not otp:
                return False, _(
                    "No active OTP request found. Please request a new code."
                )

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
