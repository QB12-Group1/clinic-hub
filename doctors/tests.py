from django.test import TestCase
from accounts.models import User
from doctors.models import Doctor, Specialty


class SpecialtyModelTests(TestCase):
    def test_str_returns_name(self):
        specialty = Specialty.objects.create(name="Cardiology")
        self.assertEqual(str(specialty), "Cardiology")


class DoctorModelTests(TestCase):
    def setUp(self):
        self.account = User.objects.create_user(phone_number="09123456789", email="test@example.com",first_name="Ali", last_name="Rezaei")  # pyright:ignore
        self.cardiology = Specialty.objects.create(name="Cardiology")
        self.dermatology = Specialty.objects.create(name="Dermatology")

    def test_doctor_creation_with_required_fields(self):
        doctor = Doctor.objects.create(
            account=self.account,
            practice_address="Tehran, Valiasr St.",
            practice_phone_number="09121112233",
            visit_fee=500000,
        )
        self.assertEqual(doctor.visit_fee, 500000)

    def test_doctor_str_uses_full_name(self):
        doctor = Doctor.objects.create(
            account=self.account,
            practice_address="Tehran",
            practice_phone_number="09121112233",
            visit_fee=500000,
        )
        self.assertEqual(str(doctor), "Dr. Ali Rezaei")

    def test_doctor_can_have_multiple_specialties(self):
        doctor = Doctor.objects.create(
            account=self.account,
            practice_address="Tehran",
            practice_phone_number="09121112233",
            visit_fee=500000,
        )
        doctor.specialties.set([self.cardiology, self.dermatology])
        self.assertEqual(doctor.specialties.count(), 2)

    def test_one_account_cannot_have_two_doctor_profiles(self):
        Doctor.objects.create(
            account=self.account,
            practice_address="Tehran",
            practice_phone_number="09121112233",
            visit_fee=500000,
        )
        with self.assertRaises(Exception):
            Doctor.objects.create(
                account=self.account,
                practice_address="Shiraz",
                practice_phone_number="09121112244",
                visit_fee=400000,
            )
