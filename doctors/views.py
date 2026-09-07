from django.db.models import QuerySet
from django.views.generic.list import ListView

from doctors.models import Doctor


class DoctorListView(ListView):
    model = Doctor
    template_name = "doctors/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Doctor]:
        queryset = (
            Doctor.objects.filter(account__is_active=True)
            .select_related("account")
            .prefetch_related("specialties")
        )
        return queryset.distinct()
