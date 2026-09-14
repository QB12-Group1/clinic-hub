from django.db.models import Q, QuerySet
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.mixins import DoctorRequiredMixins, StaffRequiredMixins
from doctors.models import Doctor, Specialty


class DoctorListView(ListView):
    model = Doctor
    template_name = "pages/list.html"
    context_object_name = "rows"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Doctor]:
        queryset = (
            Doctor.objects.filter(account__is_active=True).select_related("account").prefetch_related("specialties")
        )

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(account__first_name__icontains=query)
                | Q(account__last_name__icontains=query)
                | Q(specialties__name__icontains=query)
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Doctors",
                "nav_active": "doctors",
                "eyebrow": "Directory",
                "page_description": "Browse doctors by name or specialty.",
                "columns": [
                    {"label": "Name", "key": "full_name"},
                    {"label": "Specialties", "key": "specialty_names"},
                    {"label": "Visit Fee", "key": "visit_fee"},
                ],
                "filters": [
                    {
                        "label": "Search",
                        "name": "q",
                        "value": self.request.GET.get("q", ""),
                        "placeholder": "Name or specialty...",
                    }
                ],
                "empty_title": "No doctors found",
                "empty_description": "Try a different search term.",
                "primary_action": {
                    "label": "Add Doctor",
                    "url": reverse_lazy("doctors:create"),
                }
                if self.request.user.is_authenticated and self.request.user.is_staff  # pyright: ignore[reportAttributeAccessIssue]
                else None,
            }
        )
        return context


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "pages/detail.html"
    context_object_name = "doctor"

    def get_queryset(self) -> QuerySet[Doctor]:
        return Doctor.objects.filter(account__is_active=True).select_related("account").prefetch_related("specialties")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object
        context.update(
            {
                "page_title": doctor.full_name,
                "nav_active": "doctors",
                "eyebrow": "Doctor Profile",
                "page_description": doctor.specialty_names,
                "fields": [
                    {"label": "Biography", "value": doctor.biography or "—"},
                    {"label": "Specialties", "value": doctor.specialty_names or "—"},
                    {"label": "Visit Fee", "value": f"{doctor.visit_fee:,} Toman"},
                    {"label": "Practice Address", "value": doctor.practice_address},
                    {"label": "Practice Phone", "value": doctor.practice_phone_number},
                ],
                "back_url": reverse_lazy("doctors:list"),
                "edit_url": None,
                "delete_url": doctor.delete_url if self.request.user.is_staff else None,  # pyright: ignore[reportAttributeAccessIssue]
            }
        )
        return context


class DoctorCreateView(StaffRequiredMixins, CreateView):
    model = Doctor
    fields = ["account", "specialties", "biography", "practice_address", "practice_phone_number", "visit_fee"]
    template_name = "pages/form.html"
    success_url = reverse_lazy("doctors:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Add Doctor",
                "nav_active": "doctors",
                "eyebrow": "Directory",
                "page_description": "Create a doctor profile for an existing account.",
                "submit_label": "Create",
                "cancel_url": reverse_lazy("doctors:list"),
            }
        )
        return context


class DoctorUpdateView(DoctorRequiredMixins, UpdateView):
    model = Doctor
    fields = ["specialties", "biography", "practice_address", "practice_phone_number", "visit_fee"]
    template_name = "pages/form.html"
    success_url = reverse_lazy("doctors:list")

    def get_object(self, queryset=None):
        return self.request.user.doctor_profile  # pyright: ignore[reportAttributeAccessIssue]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Edit My Profile",
                "nav_active": "doctors",
                "eyebrow": "Doctor Profile",
                "page_description": "Update your practice information.",
                "submit_label": "Save Changes",
                "cancel_url": reverse_lazy("doctors:list"),
            }
        )
        return context


class DoctorDeleteView(StaffRequiredMixins, DeleteView):
    model = Doctor
    success_url = reverse_lazy("doctors:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Remove Doctor",
                "nav_active": "doctors",
                "eyebrow": "Directory",
                "page_description": f"Are you sure you want to remove {self.object.full_name}?",
                "submit_label": "Remove",
                "cancel_url": reverse_lazy("doctors:list"),
            }
        )
        return context


class SpecialtyListView(ListView):
    model = Specialty
    template_name = "pages/list.html"
    context_object_name = "rows"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Specialties",
                "nav_active": "specialties",
                "eyebrow": "Directory",
                "page_description": "Manage the medical specialties offered on the platform.",
                "columns": [
                    {"label": "Name", "key": "name"},
                    {"label": "Description", "key": "description"},
                ],
                "empty_title": "No specialties yet",
                "empty_description": "Add the first specialty to get started.",
                "primary_action": {
                    "label": "Add Specialty",
                    "url": reverse_lazy("doctors:specialty-create"),
                }
                if self.request.user.is_authenticated and self.request.user.is_staff  # pyright: ignore[reportAttributeAccessIssue]
                else None,
            }
        )
        return context


class SpecialtyCreateView(StaffRequiredMixins, CreateView):
    model = Specialty
    fields = ["name", "description"]
    template_name = "pages/form.html"
    success_url = reverse_lazy("doctors:specialty-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Add Specialty",
                "nav_active": "specialties",
                "eyebrow": "Directory",
                "page_description": "Create a new medical specialty.",
                "submit_label": "Create",
                "cancel_url": reverse_lazy("doctors:specialty-list"),
            }
        )
        return context


class SpecialtyUpdateView(StaffRequiredMixins, UpdateView):
    model = Specialty
    fields = ["name", "description"]
    template_name = "pages/form.html"
    success_url = reverse_lazy("doctors:specialty-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Edit Specialty",
                "nav_active": "specialties",
                "eyebrow": "Directory",
                "page_description": "Update this specialty's details.",
                "submit_label": "Save Changes",
                "cancel_url": reverse_lazy("doctors:specialty-list"),
            }
        )
        return context


class SpecialtyDeleteView(StaffRequiredMixins, DeleteView):
    model = Specialty
    success_url = reverse_lazy("doctors:specialty-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Delete Specialty",
                "nav_active": "specialties",
                "eyebrow": "Directory",
                "page_description": f'Are you sure you want to delete "{self.object.name}"?',
                "submit_label": "Delete",
                "cancel_url": reverse_lazy("doctors:specialty-list"),
            }
        )
        return context
