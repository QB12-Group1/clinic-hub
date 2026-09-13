from django.db import transaction

from appointments.models import Appointment, TimeSlot


class SlotAlreadyBookedError(Exception):
    """Raised when attempting to book a TimeSlot that is already booked."""


class AppointmentService:
    def book_time_slot(*, patient, time_slot_id: int) -> Appointment:

        with transaction.atomic():
            slot = TimeSlot.objects.select_for_update().get(pk=time_slot_id)

            if slot.is_booked:
                raise SlotAlreadyBookedError("This time slot has already been booked.")

            slot.is_booked = True
            slot.save(update_fields=["is_booked"])

            return Appointment.objects.create(
                patient=patient,
                time_slot=slot,
                is_paid=True,
                status=Appointment.Status.CONFIRMED,
            )
