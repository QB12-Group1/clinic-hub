from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


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
