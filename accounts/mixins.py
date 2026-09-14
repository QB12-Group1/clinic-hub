from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class StaffRequiredMixins(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self) -> bool | None:
        return self.request.user.is_active and self.request.user.is_staff  # pyright: ignore[reportAttributeAccessIssue]


class PatientRequiredMixins(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self) -> bool | None:
        return self.request.user.is_active and hasattr(self.request.user, "patient_profile")  # pyright: ignore[reportAttributeAccessIssue]


class DoctorRequiredMixins(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self) -> bool | None:
        return self.request.user.is_active and hasattr(self.request.user, "doctor_profile")  # pyright: ignore[reportAttributeAccessIssue]
