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

    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Required for staff and admin users. Leave blank for normal OTP users."),
    )

    email = models.EmailField(
        _("email address"),
        unique=True,
        null=True,
        blank=True,
        help_text=_("Required for regular users. Format: user@example.com"),
        error_messages={"unique": _("A user with that email already exists.")},
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
                condition=models.Q(is_staff=True, username__isnull=False, phone_number__isnull=True)
                | models.Q(is_staff=False, username__isnull=True, phone_number__isnull=False),
                name="user_has_auth_identifier",
            )
        ]

    def clean(self) -> None:
        self.username = User.normalize_username(self.username) if self.username else None  # pyright: ignore[reportAttributeAccessIssue]
        self.phone_number = utils.normalize_phone_number(self.phone_number) if self.phone_number else None

        has_username, has_phone_number = bool(self.username), bool(self.phone_number)
        if not (has_username ^ has_phone_number):
            raise ValidationError(
                _("Exactly one of username or phone number must be set (not both, not neither)."),
                code="invalid_identifiers",
            )

        super().clean()

    def save(self, *args, **kwargs) -> None:
        update_fields = kwargs.get("update_fields")

        if update_fields is None or "username" in update_fields:
            self.username = User.normalize_username(self.username) if self.username else None  # pyright: ignore[reportAttributeAccessIssue]
        if update_fields is None or "phone_number" in update_fields:
            self.phone_number = utils.normalize_phone_number(self.phone_number) if self.phone_number else None

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        identifier = self.username or self.phone_number or f"User #{self.pk or 'new'}"
        full_name = self.get_full_name().strip()
        return f"{identifier} ({full_name})" if full_name else identifier


class OTP(models.Model):
    class Purpose(models.TextChoices):
        SIGNUP = "signup", _("Signup")
        LOGIN = "login", _("Login")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        VERIFIED = "verified", _("Verified")
        REVOKED = "revoked", _("Revoked")

    phone_number = models.CharField(max_length=11)
    email = models.EmailField()
    purpose = models.CharField(max_length=32, default=Purpose.LOGIN, choices=Purpose.choices)
    status = models.CharField(max_length=16, default=Status.PENDING, choices=Status.choices, db_index=True)

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
            models.Index(fields=["phone_number", "created_at"], name="otp_phone_created_idx"),
        )
        constraints = (
            models.CheckConstraint(
                condition=models.Q(attempts_count__lte=models.F("max_attempts")),
                name="otp_attempts_within_limit",
            ),
            models.CheckConstraint(
                condition=models.Q(email__isnull=False, phone_number__isnull=False),
                name="otp_has_recipient",
            ),
        )

    def __str__(self) -> str:
        recipient = self.phone_number or self.email or "No Recipient"
        return f"OTP ({self.purpose}) - {recipient} [{self.effective_status}]"

    def save(self, *args, **kwargs) -> None:
        update_fields = kwargs.get("update_fields")

        if update_fields is None or "email" in update_fields:
            self.email = UserManager.normalize_email(self.email) if self.email else None
        if update_fields is None or "phone_number" in update_fields:
            self.phone_number = utils.normalize_phone_number(self.phone_number) if self.phone_number else None

        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        self.email = UserManager.normalize_email(self.email) if self.email else None
        self.phone_number = utils.normalize_phone_number(self.phone_number) if self.phone_number else None

        has_email, has_phone_number = bool(self.email), bool(self.phone_number)
        if not has_email or not has_phone_number:
            raise ValidationError(
                _("Both email and phone number must be provided."),
                code="invalid_recipient",
            )

        super().clean()

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()

    @property
    def is_exhausted(self) -> bool:
        return self.attempts_count >= self.max_attempts

    @property
    def is_usable(self) -> bool:
        return self.status == self.Status.PENDING and not self.is_expired and not self.is_exhausted

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
