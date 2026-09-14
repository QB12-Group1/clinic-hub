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


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "pages/detail.html"
    context_object_name = "doctor"

    def get_queryset(self) -> QuerySet[Doctor]:
        return Doctor.objects.filter(account__is_active=True).select_related("account").prefetch_related("specialties")


class DoctorCreateView(StaffRequiredMixins, CreateView):
    model = Doctor
    fields = ["account", "specialties", "biography", "practice_address", "practice_phone_number", "visit_fee"]
    template_name = "pages/create.html"
    success_url = reverse_lazy("doctors:list")


class DoctorUpdateView(DoctorRequiredMixins, UpdateView):
    model = Doctor
    fields = ["specialties", "biography", "practice_address", "practice_phone_number", "visit_fee"]
    template_name = "pages/edit.html"
    success_url = reverse_lazy("doctors:list")

    def get_object(self, queryset=None):
        return self.request.user.doctor_profile  # pyright: ignore[reportAttributeAccessIssue]


class DoctorDeleteView(StaffRequiredMixins, DeleteView):
    model = Doctor
    template_name = "pages/delete.html"
    success_url = reverse_lazy("doctors:list")


class SpecialtyListView(ListView):
    model = Specialty
    template_name = "pages/list.html"
    context_object_name = "specialties"


class SpecialtyCreateView(StaffRequiredMixins, CreateView):
    model = Specialty
    fields = ["name", "description"]
    template_name = "pages/create.html"
    success_url = reverse_lazy("doctors:specialty-list")


class SpecialtyUpdateView(StaffRequiredMixins, UpdateView):
    model = Specialty
    fields = ["name", "description"]
    template_name = "pages/edit.html"
    success_url = reverse_lazy("doctors:specialty-list")


class SpecialtyDeleteView(StaffRequiredMixins, DeleteView):
    model = Specialty
    template_name = "pages/delete.html"
    success_url = reverse_lazy("doctors:specialty-list")
