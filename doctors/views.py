from django.db.models import Q, QuerySet
from django.views.generic.list import DetailView, ListView

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
