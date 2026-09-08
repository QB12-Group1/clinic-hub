from django.db.models import QuerySet
from django.views.generic import DetailView, ListView

from doctors.models import Doctor


class DoctorListView(ListView):
    model = Doctor
    template_name = "pages/list.html"
    context_object_name = "rows"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Doctor]:
        queryset = (
            Doctor.objects.filter(account__is_active=True).select_related("account").prefetch_related("specialties")
        )
        return queryset.distinct()


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "pages/detail.html"
    context_object_name = "doctor"

    def get_queryset(self) -> QuerySet[Doctor]:
        return Doctor.objects.filter(account__is_active=True).select_related("account").prefetch_related("specialties")
