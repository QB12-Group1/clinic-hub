from django.test import TestCase

from accounts.models import User


class PatientModelTests(TestCase):
    def test_patient_linked_to_account(self):
        account = User.objects.create_user(
            phone_number="09123456789", email="test@example.com", first_name="Sara", last_name="Ahmadi"
        )  # pyright:ignore
        patient = account.patient_profile
        self.assertEqual(patient.account, account)

    def test_patient_str_includes_account(self):
        account = User.objects.create_user(
            phone_number="09123456789", email="test@example.com", first_name="Sara", last_name="Ahmadi"
        )  # pyright:ignore
        patient = account.patient_profile
        self.assertIn("Patient", str(patient))
