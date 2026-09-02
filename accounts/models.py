from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager

phone_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message=_("Phone number must be in the format '09xxxxxxxxx' (11 digits)."),
    code="invalid_phone_number",
)


class User(AbstractUser):
    username = None  # pyright: ignore[reportAssignmentType]
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class RoleChoices(models.TextChoices):
        PATIENT = "patient", _("Patient")
        DOCTOR = "doctor", _("Doctor")

    phone_number = models.CharField(
        max_length=11, unique=True, validators=[phone_validator]
    )
    role = models.CharField(
        max_length=10, choices=RoleChoices.choices, default=RoleChoices.PATIENT
    )
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()  # pyright: ignore[reportAssignmentType]

    @property
    def is_patient(self) -> bool:
        return self.role == self.RoleChoices.PATIENT

    @property
    def is_doctor(self) -> bool:
        return self.role == self.RoleChoices.DOCTOR


class OTP(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = "login", _("Login")
        EMAIL_VERIFICATION = "email_verification", _("Email Verification")
        PASSWORD_RESET = "password_reset", _("Password Reset")

    phone_number = models.CharField(max_length=11)
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
            models.Index(fields=["phone_number", "purpose", "is_used", "expires_at"]),
            models.Index(fields=["phone_number", "created_at"]),
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
        recipient = self.phone_number
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
        if not self.phone_number:
            raise ValidationError(
                _("An OTP must have an associated phone number."),
                code="missing_recipient",
            )
