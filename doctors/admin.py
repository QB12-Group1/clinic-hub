from django.contrib import admin

from doctors.models import Specialty


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    pass
