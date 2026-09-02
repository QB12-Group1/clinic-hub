from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _


class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialties = models.ManyToManyField(Specialty)
    biography = models.TextField()
    clinic_address = models.TextField()
    clinic_phone = models.CharField(max_length=11)
    visit_fee = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{_('Dr.')}{self.user.full_name}"
