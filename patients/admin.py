from typing import Any

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import ForeignKey
from django.forms import ModelChoiceField
from django.http import HttpRequest

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone_number",
        "email",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "account__email",
        "account__phone_number",
        "account__first_name",
        "account__last_name",
    )
    list_display_links = ("id", "full_name")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("account",)
    list_per_page = 25

    @admin.display(description="Name")
    def full_name(self, obj: Patient) -> str:
        return obj.account.get_full_name()

    @admin.display(description="Phone")
    def phone_number(self, obj: Patient) -> str:
        return obj.account.phone_number

    @admin.display(description="Email")
    def email(self, obj: Patient) -> str:
        return obj.account.email

    def formfield_for_foreignkey(
        self, db_field: ForeignKey[Any], request: HttpRequest, **kwargs: Any
    ) -> ModelChoiceField | None:
        User = get_user_model()
        if db_field.name == "account":
            User = get_user_model()
            base_qs = User.objects.filter(
                is_staff=False,
                is_superuser=False,
                phone_number__isnull=False,
                patient_profile__isnull=True,
            )

            patient_id: str | None = None
            if request.resolver_match:
                patient_id = request.resolver_match.kwargs.get("object_id")

            if patient_id:
                base_qs = base_qs | User.objects.filter(patient_profile__id=patient_id)

            kwargs["queryset"] = base_qs

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
