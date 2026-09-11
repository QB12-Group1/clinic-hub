from django.test import TestCase
from accounts.models import User
from patients.models import Patient


class PatientModelTests(TestCase):
    def test_patient_linked_to_account(self):
        account = User.objects.create_user(phone_number="09123456789", email="test@example.com",first_name="Sara", last_name="Ahmadi")  # pyright:ignore
        patient = Patient.objects.create(account=account)
        self.assertEqual(patient.account, account)

    def test_patient_str_includes_account(self):
        account = User.objects.create_user(phone_number="09123456789", email="test@example.com",first_name="Sara", last_name="Ahmadi")  # pyright:ignore
        patient = Patient.objects.create(account=account)
        self.assertIn("Patient", str(patient))
