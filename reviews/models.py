from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    appointment = models.OneToOneField("appointments.Appointment", related_name="review", on_delete=models.PROTECT)
    comment = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="review_rating_between_1_and_5",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.appointment.time_slot.doctor} - {self.rating}/5"
