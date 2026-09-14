from django.db import models
from django.urls import reverse_lazy

from core import settings


# TODO: we should support gender and national id later
class Patient(models.Model):
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="patient_profile",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Patient: {self.account}"

    @property
    def full_name(self):
        return self.account.get_full_name()

    @property
    def email(self):
        return self.account.email

    @property
    def phone_number(self):
        return self.account.phone_number

    @property
    def detail_url(self):
        return reverse_lazy("patients:detail", kwargs={"pk": self.pk})

    @property
    def edit_url(self):
        return reverse_lazy("patients:edit", kwargs={"pk": self.pk})

    @property
    def delete_url(self):
        return reverse_lazy("patients:delete", kwargs={"pk": self.pk})
