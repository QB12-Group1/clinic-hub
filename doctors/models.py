from django.conf import settings
from django.db import models

from validators import PhoneNumberValidator


class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


# TODO: separate practice information into it's own model
class Doctor(models.Model):
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="doctor_profile",
        on_delete=models.CASCADE,
    )
    specialties = models.ManyToManyField(Specialty, blank=True, related_name="doctors")
    biography = models.TextField(blank=True)
    practice_address = models.TextField()
    practice_phone_number = models.CharField(
        max_length=11, validators=[PhoneNumberValidator()]
    )
    visit_fee = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Dr. {self.account.get_full_name()}"
