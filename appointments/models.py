from django.db import models


class TimeSlot(models.Model):
    doctor = models.ForeignKey(
        "doctors.Doctor", related_name="time_slots", on_delete=models.CASCADE
    )
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
        return (
            f"Dr. {self.doctor.account.get_full_name()} -"
            f"{self.start_time:%Y-%m-%d %H:%M} ({status})"
        )
