from django.db import models

from core import settings


# TODO: we should support gender and national id later
class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="patient_profile",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Patient: {self.user}"
