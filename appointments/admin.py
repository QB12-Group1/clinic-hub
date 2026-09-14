from typing import Any

from django.contrib import admin

from .models import Appointment, TimeSlot


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "doctor",
        "start_time",
        "end_time",
        "duration_display",
        "is_booked",
    )
    list_filter = (
        "is_booked",
        "start_time",
        ("doctor", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "doctor__account__first_name",
        "doctor__account__last_name",
        "doctor__account__phone_number",
        "doctor__account__username",
    )
    autocomplete_fields = ("doctor",)
    date_hierarchy = "start_time"
    list_select_related = ("doctor__account",)
    list_per_page = 25

    @admin.display(description="Duration")
    def duration_display(self, obj: TimeSlot) -> str:
        if obj.start_time and obj.end_time:
            mins = int((obj.end_time - obj.start_time).total_seconds() // 60)
            return f"{mins} min"
        return "-"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "doctor",
        "patient",
        "start_time",
        "end_time",
        "duration_display",
        "is_paid",
        "status",
    )
    list_filter = (
        "is_paid",
        "status",
        "time_slot__start_time",
        ("patient", admin.RelatedOnlyFieldListFilter),
        ("time_slot__doctor", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "patient__account__first_name",
        "patient__account__last_name",
        "patient__account__phone_number",
        "time_slot__doctor__account__first_name",
        "time_slot__doctor__account__last_name",
    )
    autocomplete_fields = ("patient", "time_slot")
    date_hierarchy = "time_slot__start_time"
    list_select_related = (
        "patient__account",
        "time_slot__doctor__account",
    )
    list_per_page = 25

    @admin.display(description="Doctor", ordering="time_slot__doctor")
    def doctor(self, obj: Appointment) -> Any:
        return obj.time_slot.doctor if obj.time_slot else "-"

    @admin.display(description="Start Time", ordering="time_slot__start_time")
    def start_time(self, obj: Appointment) -> Any:
        return obj.time_slot.start_time if obj.time_slot else "-"

    @admin.display(description="End Time", ordering="time_slot__end_time")
    def end_time(self, obj: Appointment) -> Any:
        return obj.time_slot.end_time if obj.time_slot else "-"

    @admin.display(description="Duration")
    def duration_display(self, obj: Appointment) -> str:
        if obj.time_slot and obj.time_slot.start_time and obj.time_slot.end_time:
            mins = int((obj.time_slot.end_time - obj.time_slot.start_time).total_seconds() // 60)
            return f"{mins} min"
        return "-"
