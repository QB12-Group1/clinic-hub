from typing import cast

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import utils
from accounts.managers import UserManager
from validators import PhoneNumberValidator


class User(AbstractUser):
    REQUIRED_FIELDS = []

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=_(
            "Required for staff and admin users. Leave blank for normal OTP users."
        ),
    )

    phone_number = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        validators=[PhoneNumberValidator()],
        help_text=_("Required for regular users. Format: 09123456789"),
        error_messages={"unique": _("A user with that phone number already exists.")},
    )

    objects = UserManager()  # pyright: ignore[reportAssignmentType]

    class Meta(AbstractUser.Meta):
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    is_staff=True, username__isnull=False, phone_number__isnull=True
                )
                | models.Q(
                    is_staff=False, username__isnull=True, phone_number__isnull=False
                ),
                name="user_has_auth_identifier",
            )
        ]

    def clean(self) -> None:
        self.username = self.username or None  # pyright: ignore[reportAttributeAccessIssue]
        self.phone_number = (
            utils.normalize_phone_number(self.phone_number)
            if self.phone_number
            else None
        )
        super().clean()

        if self.is_staff and not self.username:
            raise ValidationError(
                {"username": _("Staff and admin users must have a username.")}
            )

        if not self.is_staff and not self.phone_number:
            raise ValidationError(
                {"phone_number": _("Regular users must have a phone number.")}
            )

    def save(self, *args, **kwargs) -> None:
        self.username = self.username or None  # pyright: ignore[reportAttributeAccessIssue]
        self.phone_number = (
            utils.normalize_phone_number(self.phone_number)
            if self.phone_number
            else None
        )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        identifier = self.username or self.phone_number or f"User #{self.pk or 'new'}"
        full_name = self.get_full_name().strip()

        if full_name:
            return f"{identifier} ({full_name})"
        return identifier


class OTP(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = "login", _("Login")
        PASSWORD_RESET = "password_reset", _("Password Reset")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        VERIFIED = "verified", _("Verified")
        REVOKED = "revoked", _("Revoked")

    phone_number = models.CharField(max_length=11)
    purpose = models.CharField(
        max_length=32, default=Purpose.LOGIN, choices=Purpose.choices
    )
    status = models.CharField(
        max_length=16, default=Status.PENDING, choices=Status.choices, db_index=True
    )

    code = models.CharField(max_length=128)
    attempts_count = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)

    expires_at = models.DateTimeField(db_index=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        ordering = ["-created_at"]
        indexes = (
            models.Index(
                fields=["phone_number", "purpose", "status", "expires_at"],
                name="otp_lookup_idx",
            ),
            models.Index(
                fields=["phone_number", "created_at"], name="otp_phone_created_idx"
            ),
        )
        constraints = (
            models.CheckConstraint(
                condition=~models.Q(phone_number=""),
                name="otp_has_recipient",
            ),
            models.CheckConstraint(
                condition=models.Q(attempts_count__lte=models.F("max_attempts")),
                name="otp_attempts_within_limit",
            ),
        )

    def __str__(self) -> str:
        return f"OTP ({self.purpose}) - {self.phone_number} [{self.effective_status}]"

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()

    @property
    def is_exhausted(self) -> bool:
        return self.attempts_count >= self.max_attempts

    @property
    def is_usable(self) -> bool:
        return (
            self.status == self.Status.PENDING
            and not self.is_expired
            and not self.is_exhausted
        )

    @property
    def effective_status(self) -> str:
        if self.status == self.Status.VERIFIED:
            val = self.Status.VERIFIED.label
        elif self.status == self.Status.REVOKED:
            val = self.Status.REVOKED.label
        elif self.is_exhausted:
            val = _("Exhausted")
        elif self.is_expired:
            val = _("Expired")
        else:
            val = self.Status.PENDING.label

        return cast(str, val)

    def set_code(self, raw_code: str) -> None:
        self.code = make_password(raw_code)

    def check_code(self, raw_code: str) -> bool:
        return check_password(raw_code, self.code)

    def clean(self) -> None:
        super().clean()
        if not self.phone_number:
            raise ValidationError(
                _("An OTP must have an associated phone number."),
                code="missing_recipient",
            )
