from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

phone_validator = RegexValidator(
    regex=r"^0\d{10}$",
    message=_("Phone number must start with 0 and contain exactly 11 digits."),
    code="invalid_phone_number",
)


class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialties = models.ManyToManyField(Specialty, blank=True, related_name="doctors")
    biography = models.TextField(blank=True)
    clinic_address = models.TextField()
    clinic_phone_number = models.CharField(max_length=11, validators=[phone_validator])
    visit_fee = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Dr. {self.user.get_full_name()}"
