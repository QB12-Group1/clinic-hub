from datetime import timedelta
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from appointments.models import Appointment, TimeSlot
from doctors.models import Doctor
from patients.models import Patient


class TimeSlotModelTests(TestCase):
    def setUp(self):
        account = User.objects.create_user(phone_number="09123456789", first_name="Ali", last_name="Rezaei")  # pyright:ignore[reportCallIssue]
        self.doctor = Doctor.objects.create(
            account=account, practice_address="Tehran", practice_phone_number="09121112233", visit_fee=500000
        )
        self.now = timezone.now()

    def test_valid_time_slot_creation(self):
        slot = TimeSlot.objects.create(
            doctor=self.doctor, start_time=self.now, end_time=self.now + timedelta(minutes=30)
        )
        self.assertFalse(slot.is_booked)

    def test_end_time_must_be_after_start_time(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TimeSlot.objects.create(
                    doctor=self.doctor,
                    start_time=self.now,
                    end_time=self.now - timedelta(minutes=30),
                )


class AppointmentModelTests(TestCase):
    def setUp(self):
        doctor_account = User.objects.create_user(phone_number="09123456789", first_name="Ali", last_name="Rezaei")  # pyright:ignore[reportCallIssue]
        self.doctor = Doctor.objects.create(
            account=doctor_account, practice_address="Tehran", practice_phone_number="09121112233", visit_fee=500000
        )
        patient_account = User.objects.create_user(phone_number="09121234567", first_name="Sara", last_name="Ahmadi")  # pyright:ignore[reportCallIssue]
        self.patient = Patient.objects.create(account=patient_account)
        now = timezone.now()
        self.slot = TimeSlot.objects.create(doctor=self.doctor, start_time=now, end_time=now + timedelta(minutes=30))

    def test_appointment_creation(self):
        appointment = Appointment.objects.create(patient=self.patient, time_slot=self.slot)
        self.assertIsNotNone(appointment.pk)
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.time_slot, self.slot)
        self.assertEqual(appointment.status, Appointment.Status.PENDING)

    def test_cannot_have_two_active_appointments_on_same_slot(self):
        Appointment.objects.create(patient=self.patient, time_slot=self.slot, status=Appointment.Status.CONFIRMED)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Appointment.objects.create(
                    patient=self.patient, time_slot=self.slot, status=Appointment.Status.CONFIRMED
                )

        self.assertEqual(Appointment.objects.filter(time_slot=self.slot).count(), 1)

    def test_canceling_frees_the_slot_for_a_new_appointment(self):
        first = Appointment.objects.create(
            patient=self.patient, time_slot=self.slot, status=Appointment.Status.CONFIRMED
        )
        first.status = Appointment.Status.CANCELED
        first.save()
        first.refresh_from_db()

        self.assertEqual(first.status, Appointment.Status.CANCELED)

        second = Appointment.objects.create(
            patient=self.patient, time_slot=self.slot, status=Appointment.Status.CONFIRMED
        )
        self.assertIsNotNone(second.pk)
        self.assertEqual(second.time_slot, self.slot)
        self.assertEqual(second.status, Appointment.Status.CONFIRMED)
