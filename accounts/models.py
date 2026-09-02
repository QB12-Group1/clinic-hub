from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core import settings


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = "admin", _("Admin")
        PATIENT = "patient", _("Patient")
        DOCTOR = "doctor", _("Doctor")

    role = models.CharField(
        max_length=10, choices=RoleChoices.choices, default=RoleChoices.PATIENT
    )

    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_admin(self) -> bool:
        return self.role == self.RoleChoices.ADMIN

    @property
    def is_patient(self) -> bool:
        return self.role == self.RoleChoices.PATIENT

    @property
    def is_doctor(self) -> bool:
        return self.role == self.RoleChoices.DOCTOR

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class OTP(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = "login", _("Login")
        EMAIL_VERIFICATION = "email_verification", _("Email Verification")
        PASSWORD_RESET = "password_reset", _("Password Reset")

    email = models.CharField(default="", max_length=256, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="otps",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    purpose = models.CharField(
        max_length=32, default=Purpose.LOGIN, choices=Purpose.choices
    )

    code = models.CharField(max_length=128)
    attempts_count = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)

    expires_at = models.DateTimeField(db_index=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        ordering = ["-created_at"]
        indexes = (
            models.Index(fields=["email", "purpose", "is_used", "expires_at"]),
            models.Index(fields=["user", "purpose", "is_used", "expires_at"]),
            models.Index(fields=["email", "created_at"]),
        )
        constraints = (
            models.CheckConstraint(
                condition=models.Q(user__isnull=False) | ~models.Q(email=""),
                name="otp_has_recipient",
            ),
            models.CheckConstraint(
                condition=models.Q(attempts_count__lte=models.F("max_attempts")),
                name="otp_attempts_within_limit",
            ),
        )

    def __str__(self) -> str:
        recipient = self.user.get_username() if self.user else self.email
        status = "Used" if self.is_used else "Active/Unused"
        return f"OTP [{self.purpose}] for {recipient or 'Unknown'} ({status})"

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()

    def set_code(self, raw_code: str) -> None:
        self.code = make_password(raw_code)

    def check_code(self, raw_code: str) -> bool:
        return check_password(raw_code, self.code)

    def clean(self) -> None:
        super().clean()
        if not self.user and not self.email:
            raise ValidationError(
                _("An OTP must have an associated user or email."),
                code="missing_recipient",
            )
