from django.contrib import admin

from doctors.models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "get_specialties",
        "visit_fee",
    )
    list_filter = ("specialties",)
    search_fields = (
        "account__first_name",
        "account__last_name",
    )

    @admin.display(description="Specialties")
    def get_specialties(self, obj):
        return ", ".join([s.name for s in obj.specialties.all()])
