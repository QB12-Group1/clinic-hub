from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from django.views.generic.edit import DeleteView

from accounts.mixins import PatientRequiredMixins, StaffRequiredMixins
from appointments.models import Appointment, TimeSlot
from doctors.models import Doctor
from reviews.models import Review

from .models import Patient

User = get_user_model()


class PatientHomeView(PatientRequiredMixins, TemplateView):
    template_name = "pages/patient_home.html"

    @staticmethod
    def _safe_reverse(view_name: str, **kwargs: str) -> str | None:
        try:
            return reverse(view_name, kwargs=kwargs)
        except NoReverseMatch:
            return None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        patient_profile = user.patient_profile  # pyright: ignore[reportAttributeAccessIssue]
        wallet = user.wallet  # pyright: ignore[reportAttributeAccessIssue]
        now = timezone.now()

        next_appointment = (
            patient_profile.appointments.select_related("time_slot")
            .filter(time_slot__start_time__gte=now)
            .exclude(status=Appointment.Status.CANCELED)
            .order_by("time_slot__start_time")
            .first()
        )
        reviews_count = Review.objects.filter(appointment__patient=patient_profile).count()
        active_appointments_count = patient_profile.appointments.exclude(status=Appointment.Status.CANCELED).count()
        doctors = Doctor.objects.select_related("account").prefetch_related("specialties").all()
        available_slots = TimeSlot.objects.select_related("doctor__account").filter(is_booked=False)

        recent_appointments = (
            patient_profile.appointments.select_related("time_slot")
            .filter(status=Appointment.Status.CONFIRMED, time_slot__start_time__lte=now)
            .order_by("-time_slot__start_time")
        )

        for appointment in recent_appointments:
            appointment.has_review = hasattr(appointment, "review")
            appointment.review_url = "#"
            appointment.can_review = (
                appointment.status == Appointment.Status.CONFIRMED
                and appointment.time_slot.start_time <= now
                and not appointment.has_review
            )

        context.update(
            {
                "page_title": "Patient home",
                "nav_active": "appointments",
                "user": user,
                "wallet": wallet,
                "next_appointment": next_appointment,
                "reviews_count": reviews_count,
                "active_appointments_count": active_appointments_count,
                "doctors": doctors,
                "available_slots": available_slots,
                "recent_appointments": recent_appointments,
                "top_up_wallet_url": self._safe_reverse("wallet:top-up"),
            }
        )
        return context


class PatientListView(ListView):
    model = Patient
    template_name = "pages/list.html"
    context_object_name = "rows"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Patient]:
        patients = super().get_queryset().select_related("account")
        query = self.request.GET.get("q", "").strip()
        if patients:
            patients = patients.filter(
                Q(account__first_name__icontains=query)
                | Q(account__last_name__icontains=query)
                | Q(account__phone_number=query)
                | Q(account__email=query)
            )
        return patients

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Patients",
                "nav_active": "patients",
                "eyebrow": "Patient list",
                "page_description": "View patients",
                "primary_action": {
                    "label": "Add patient",
                    "url": reverse_lazy("patients:create"),
                },
                "columns": [
                    {"label": "Name", "key": "full_name"},
                    {"label": "Email", "key": "email"},
                    {"label": "Phone", "key": "phone_number"},
                ],
                "filters": [
                    {
                        "label": "Search",
                        "name": "q",
                        "value": self.request.GET.get("q", ""),
                        "placeholder": "Name, email or phone number",
                    }
                ],
                "empty_title": "No patients found",
                "empty_description": "Try clearing the search or add a patient.",
            }
        )
        return context


class PatientCreateView(StaffRequiredMixins, CreateView):
    model = User
    template_name = "pages/form.html"
    fields = ("first_name", "last_name", "email", "phone_number")

    def get_success_url(self) -> str:
        return reverse("patients:detail", kwargs={"pk": self.object.patient_profile.id})  # pyright: ignore[reportOptionalMemberAccess]

    def form_valid(self, form: ModelForm) -> HttpResponse:
        self.object = self.model.objects.create_user(**form.cleaned_data)
        messages.success(self.request, f"Patient {self.object.get_full_name()} created.")  # pyright: ignore[reportOptionalMemberAccess]
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Add New Patient",
                "nav_active": "patients",
                "eyebrow": "Patient Directory",
                "page_description": "Register a new patient account and contact profile.",
                "submit_label": "Create Patient",
                "cancel_url": reverse("patients:list"),
            }
        )
        return context


class PatientDetailView(DetailView):
    model = User
    template_name = "pages/detail.html"
    context_object_name = "patient"

    def get_queryset(self) -> QuerySet[Patient]:
        return super().get_queryset().select_related("account")

    def get_object(self, queryset=None):
        patient = get_object_or_404(Patient.objects.select_related("account"), pk=self.kwargs["pk"])
        self.patient = patient
        return patient.account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object
        context.update(
            {
                "page_title": patient.get_full_name(),
                "nav_active": "patients",
                "eyebrow": "Patient Profile",
                "fields": [
                    {"label": "Full name", "value": patient.get_full_name()},
                    {"label": "Email", "value": patient.email},
                    {"label": "Phone number", "value": patient.phone_number},
                ],
                "back_url": reverse_lazy("patients:list"),
                "edit_url": reverse_lazy("patients:edit", kwargs={"pk": self.patient.pk}),
                "delete_url": reverse_lazy("patients:delete", kwargs={"pk": self.patient.pk}),
            }
        )
        return context


class PatientEditView(StaffRequiredMixins, UpdateView):
    model = User
    fields = ("first_name", "last_name", "email", "phone_number")
    template_name = "pages/form.html"
    success_url = reverse_lazy("patients:list")

    def get_object(self, queryset=None):
        patient = get_object_or_404(Patient.objects.select_related("account"), pk=self.kwargs["pk"])
        self.patient = patient
        return patient.account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": f"Edit {self.patient.full_name}",
                "nav_active": "patients",
                "eyebrow": "Patients",
                "page_description": "Update personal information, contact details, and more.",
                "submit_label": "Save changes",
                "cancel_url": reverse_lazy("patients:list"),
            }
        )
        return context


class PatientDeleteView(StaffRequiredMixins, DeleteView):
    model = User
    context_object_name = "patient"
    success_url = reverse_lazy("patients:list")

    def get_queryset(self) -> QuerySet[Patient]:
        return super().get_queryset().select_related("account")

    def get_object(self, queryset=None):
        patient = get_object_or_404(Patient.objects.select_related("account"), pk=self.kwargs["pk"])
        self.patient = patient
        return patient.account

    def form_valid(self, form):
        full_name = self.object.get_full_name()
        response = super().form_valid(form)
        messages.success(self.request, f"Patient {full_name} deleted.")
        return response
