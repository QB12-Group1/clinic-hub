from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeSlot(models.Model):
    doctor = models.ForeignKey("doctors.Doctor", related_name="time_slots", on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        constraints = (
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="timeslot_end_after_start",
            ),
        )

        indexes = (
            models.Index(
                fields=["doctor", "is_booked", "start_time"],
                name="timeslot_availablitiy_idx",
            ),
        )

    def __str__(self) -> str:
        status = "Booked" if self.is_booked else "Available"
        return f"{self.doctor} -{self.start_time:%Y-%m-%d %H:%M} ({status})"


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        CANCELED = "canceled", _("Canceled")

    patient = models.ForeignKey("patients.Patient", related_name="appointments", on_delete=models.PROTECT)
    time_slot = models.ForeignKey(TimeSlot, related_name="appointments", on_delete=models.PROTECT)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["time_slot"],
                condition=~models.Q(status="canceled"),
                name="unique_active_appointment_per_slot",
            )
        ]

    def __str__(self) -> str:
        return f"Appointment #{self.pk} - {self.patient} at {self.time_slot}"
