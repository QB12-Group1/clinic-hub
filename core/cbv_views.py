"""Class-based view equivalents of the function-based examples in
``core/views.py``. These are wired up under ``/ui/examples-cbv/patients/``
so they can be compared side-by-side without touching the original routes.

The example "patients" are plain dictionaries (not a Django model), so a
couple of the generic views are adapted slightly:

- ``PatientListView`` overrides ``get_queryset`` to return a filtered list
  instead of a real queryset. ``ListView`` is happy to paginate any
  sequence, so this works the same as it would with ``Patient.objects.all()``.
- ``PatientDetailView`` overrides ``get_object`` because there is no model
  manager to look the row up with.
- ``PatientCreateView``/``PatientUpdateView`` use ``FormView`` instead of
  ``CreateView``/``UpdateView`` since ``PatientExampleForm`` is a plain
  ``forms.Form``, not a ``ModelForm``. With a real model you would just use
  ``CreateView``/``UpdateView`` directly and drop the ``get_initial``/
  ``form_valid`` overrides shown here.
- ``PatientDeleteView`` mirrors ``DeleteView`` but only needs a ``post``
  handler since the confirmation UI is the ``confirm_modal.html`` component
  on the list/detail pages rather than a dedicated confirmation template.
"""

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from core.forms import PatientExampleForm
from core.views import EXAMPLE_PATIENTS


def _get_patient_or_none(patient_id):
    return next((item for item in EXAMPLE_PATIENTS if item["id"] == patient_id), None)


class PatientListView(ListView):
    template_name = "pages/list.html"
    context_object_name = "rows"
    paginate_by = 10

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        query = self.request.GET.get("q", "").strip().lower()
        patients = EXAMPLE_PATIENTS
        if query:
            patients = [
                patient for patient in patients if query in patient["name"].lower() or query in patient["phone"]
            ]
        return [
            {
                **patient,
                "detail_url": reverse("cbv-patient-detail", args=[patient["id"]]),
                "edit_url": reverse("cbv-patient-edit", args=[patient["id"]]),
                "delete_url": reverse("cbv-patient-delete", args=[patient["id"]]),
            }
            for patient in patients
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Patients",
                "nav_active": "patients",
                "eyebrow": "Reusable list example (CBV)",
                "page_description": "The same table/filter/pagination UI, "
                "driven by a ListView instead of a plain function view.",
                "primary_action": {
                    "label": "Add patient",
                    "url": reverse("cbv-patient-create"),
                },
                "columns": [
                    {"label": "Name", "key": "name"},
                    {"label": "Phone", "key": "phone"},
                    {"label": "Status", "key": "status"},
                ],
                "filters": [
                    {
                        "label": "Search",
                        "name": "q",
                        "value": self.request.GET.get("q", ""),
                        "placeholder": "Name or phone",
                    }
                ],
                "empty_title": "No patients found",
                "empty_description": "Try clearing the search or add a patient.",
            }
        )
        return context


class PatientDetailView(DetailView):
    template_name = "pages/detail.html"
    context_object_name = "patient"

    def get_object(self, queryset=None):
        patient = _get_patient_or_none(self.kwargs["patient_id"])
        if patient is None:
            raise ImproperlyConfigured("No example patient with that id.")
        return patient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object
        context.update(
            {
                "page_title": patient["name"],
                "nav_active": "patients",
                "eyebrow": "Reusable detail example (CBV)",
                "fields": [
                    {"label": "Full name", "value": patient["name"]},
                    {"label": "Phone number", "value": patient["phone"]},
                    {"label": "Status", "value": patient["status"]},
                ],
                "back_url": reverse("cbv-patient-list"),
                "edit_url": reverse("cbv-patient-edit", args=[patient["id"]]),
                "delete_url": reverse("cbv-patient-delete", args=[patient["id"]]),
            }
        )
        return context


class PatientFormView(SuccessMessageMixin, FormView):
    """Shared create/update view: with a real ModelForm you would instead
    use CreateView/UpdateView and delete most of this class."""

    template_name = "pages/form.html"
    form_class = PatientExampleForm
    success_url = reverse_lazy("cbv-patient-list")
    success_message = "Example form validated successfully. Connect it to your model's save() next."

    def dispatch(self, request, *args, **kwargs):
        self.patient = _get_patient_or_none(kwargs.get("patient_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        if not self.patient:
            return super().get_initial()
        first_name, _, last_name = self.patient["name"].partition(" ")
        return {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": self.patient["phone"],
            "active": True,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Edit patient" if self.patient else "Add patient",
                "nav_active": "patients",
                "eyebrow": "Reusable form example (CBV)",
                "page_description": "The same template works with any Django Form or ModelForm.",
                "submit_label": "Save patient",
                "cancel_url": reverse("cbv-patient-list"),
            }
        )
        return context

    def form_valid(self, form):
        # With a real ModelForm this is just `form.save()`.
        return super().form_valid(form)


class PatientDeleteView(View):
    """No confirmation template is needed: the trigger button and confirm
    dialog both live in components/confirm_modal.html, included from the
    list and detail pages."""

    def post(self, request, patient_id):
        EXAMPLE_PATIENTS[:] = [item for item in EXAMPLE_PATIENTS if item["id"] != patient_id]
        messages.success(request, "Example patient deleted.")
        return redirect("cbv-patient-list")
