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
        account = User.objects.create_user(phone_number="09123456789", first_name="Ali", last_name="Rezaei") #pyright:ignore
        self.doctor = Doctor.objects.create( account=account, practice_address="Tehran", practice_phone_number="09121112233", visit_fee=500000 ) 
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
    