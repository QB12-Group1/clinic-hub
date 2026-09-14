from django.contrib.auth.models import BaseUserManager

import utils
from patients.models import Patient
from wallet.models import Wallet


class UserManager(BaseUserManager):
    def _create_user(
        self,
        username: str | None = None,
        email: str | None = None,
        phone_number: str | None = None,
        password: str | None = None,
        **extra_fields,
    ):
        username = self.model.normalize_username(username) if username else None
        email = BaseUserManager.normalize_email(email) if email else None
        phone_number = utils.normalize_phone_number(phone_number) if phone_number else None
        user, _ = self.get_or_create(username=username, email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email: str, phone_number: str, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        if extra_fields.get("is_staff"):
            raise ValueError("Regular user must have is_staff=False")
        if extra_fields.get("is_superuser"):
            raise ValueError("Regular user must have is_superuser=False")

        if not email:
            raise ValueError("The given email must be set")

        if not phone_number:
            raise ValueError("The given phone number must be set")

        account = self._create_user(email=email, phone_number=phone_number, **extra_fields)
        Patient.objects.get_or_create(account=account)
        Wallet.objects.get_or_create(account=account)
        return account

    def create_staff_user(self, username: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)

        if not extra_fields.get("is_staff"):
            raise ValueError("Staff user must have is_staff=True")
        if extra_fields.get("is_superuser"):
            raise ValueError("Staff user must have is_superuser=False")

        return self._create_user(username=username, password=password, **extra_fields)

    def create_superuser(self, username: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(username=username, password=password, **extra_fields)
