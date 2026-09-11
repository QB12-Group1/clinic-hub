from django.test import TestCase
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.utils import timezone
from accounts.models import User
from appointments.models import Appointment, TimeSlot
from doctors.models import Doctor
from patients.models import Patient
from reviews.models import Review


class ReviewModelTests(TestCase):
    def setUp(self):
        doctor_account = User.objects.create_user(phone_number="09123456789", email="doctor@example.com",first_name="Ali", last_name="Rezaei")  # pyright: ignore[reportCallIssue]
        self.doctor = Doctor.objects.create(
            account=doctor_account,
            practice_address="Tehran",
            practice_phone_number="09121112233",
            visit_fee=500000,
        )
        patient_account = User.objects.create_user(phone_number="09121234567",email="patient@example.com", first_name="Zahra", last_name="Roshan")  # pyright: ignore[reportCallIssue]
        self.patient = Patient.objects.create(account=patient_account)

        now = timezone.now()
        self.slot = TimeSlot.objects.create(doctor=self.doctor, start_time=now, end_time=now + timedelta(minutes=30))
        self.appointment = Appointment.objects.create(
            patient=self.patient, time_slot=self.slot, status=Appointment.Status.CONFIRMED
        )

    def test_review_creation_with_valid_data(self):
        review = Review.objects.create(appointment=self.appointment, rating=5, comment="Great doctor!")
        self.assertIsNotNone(review.pk)
        self.assertEqual(review.appointment, self.appointment)
        self.assertEqual(review.rating, 5)

    def test_one_appointment_cannot_have_two_reviews(self):
        Review.objects.create(appointment=self.appointment, rating=5)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(appointment=self.appointment, rating=3)

    def test_rating_must_be_between_one_and_five(self):
        with self.assertRaises(ValidationError):
            Review(appointment=self.appointment, rating=0).full_clean()
        with self.assertRaises(ValidationError):
            Review(appointment=self.appointment, rating=6).full_clean()

    def test_database_constraint_blocks_out_of_range_rating_bypassing_full_clean(self):
        review = Review.objects.create(appointment=self.appointment, rating=5)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.filter(pk=review.pk).update(rating=10)

    def test_cannot_delete_appointment_that_has_a_review(self):
        Review.objects.create(appointment=self.appointment, rating=5)
        with self.assertRaises(ProtectedError):
            self.appointment.delete()
