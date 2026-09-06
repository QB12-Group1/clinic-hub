from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from core.forms import PatientExampleForm

EXAMPLE_PATIENTS = [
    {"id": 1, "name": "Mina Rahimi", "phone": "09121234567", "status": "Active"},
    {"id": 2, "name": "Reza Moradi", "phone": "09123334455", "status": "Active"},
    {"id": 3, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 4, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 5, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 6, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 7, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 8, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 9, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 10, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 20, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
    {"id": 30, "name": "Sara Ahmadi", "phone": "09127778899", "status": "Follow-up"},
]


def dashboard(request):
    context = {
        "stats": [
            {
                "label": "Appointments today",
                "value": "24",
                "change": "+8.2%",
                "icon": "calendar-check-2",
                "tone": "primary",
            },
            {
                "label": "Active patients",
                "value": "1,284",
                "change": "+12.5%",
                "icon": "users",
                "tone": "secondary",
            },
            {
                "label": "Revenue this month",
                "value": "$18.6k",
                "change": "+6.4%",
                "icon": "wallet-cards",
                "tone": "accent",
            },
            {
                "label": "Avg. satisfaction",
                "value": "4.9",
                "change": "+0.3",
                "icon": "star",
                "tone": "violet-500",
            },
        ],
        "appointments": [
            {
                "time": "09:00",
                "patient": "Mina Rahimi",
                "type": "Follow-up",
                "doctor": "Dr. Arman Sadeghi",
                "status": "Confirmed",
                "status_tone": "success",
                "tone": "primary",
            },
            {
                "time": "10:30",
                "patient": "Reza Moradi",
                "type": "Initial consultation",
                "doctor": "Dr. Niloofar Kamali",
                "status": "Checked in",
                "status_tone": "info",
                "tone": "secondary",
            },
            {
                "time": "13:00",
                "patient": "Sara Ahmadi",
                "type": "Routine checkup",
                "doctor": "Dr. Arman Sadeghi",
                "status": "Confirmed",
                "status_tone": "success",
                "tone": "accent",
            },
            {
                "time": "15:30",
                "patient": "Omid Karimi",
                "type": "Lab results",
                "doctor": "Dr. Niloofar Kamali",
                "status": "Pending",
                "status_tone": "warning",
                "tone": "secondary",
            },
        ],
        "bars": [
            {"day": "Mon", "height": 75, "fill": 68},
            {"day": "Tue", "height": 90, "fill": 82},
            {"day": "Wed", "height": 65, "fill": 54},
            {"day": "Thu", "height": 100, "fill": 88},
            {"day": "Fri", "height": 80, "fill": 72},
            {"day": "Sat", "height": 48, "fill": 38},
            {"day": "Sun", "height": 30, "fill": 22},
        ],
        "doctors": [
            {
                "name": "Dr. Arman Sadeghi",
                "specialty": "Cardiology",
                "initials": "AS",
                "tone": "primary",
            },
            {
                "name": "Dr. Niloofar Kamali",
                "specialty": "Family medicine",
                "initials": "NK",
                "tone": "secondary",
            },
            {
                "name": "Dr. Pouya Etemadi",
                "specialty": "Dermatology",
                "initials": "PE",
                "tone": "accent",
            },
        ],
        "nav_active": "overview",
    }
    return render(request, "dashboard.html", context)


def patient_examples(request):
    query = request.GET.get("q", "").strip().lower()
    patients = EXAMPLE_PATIENTS
    if query:
        patients = [patient for patient in patients if query in patient["name"].lower() or query in patient["phone"]]
    rows = [
        {
            **patient,
            "detail_url": f"/ui/examples/patients/{patient['id']}/",
            "edit_url": f"/ui/examples/patients/{patient['id']}/edit/",
            "delete_url": f"/ui/examples/patients/{patient['id']}/delete/",
        }
        for patient in patients
    ]
    page_obj = Paginator(rows, 10).get_page(request.GET.get("page"))
    return render(
        request,
        "pages/list.html",
        {
            "page_title": "Patients",
            "nav_active": "patients",
            "eyebrow": "Reusable list example",
            "page_description": "A generic table, filter, empty state, pagination, and row actions.",
            "primary_action": {
                "label": "Add patient",
                "url": "/ui/examples/patients/new/",
            },
            "columns": [
                {"label": "Name", "key": "name"},
                {"label": "Phone", "key": "phone"},
                {"label": "Status", "key": "status"},
            ],
            "rows": page_obj.object_list,
            "page_obj": page_obj,
            "filters": [
                {
                    "label": "Search",
                    "name": "q",
                    "value": request.GET.get("q", ""),
                    "placeholder": "Name or phone",
                }
            ],
            "empty_title": "No patients found",
            "empty_description": "Try clearing the search or add a patient.",
        },
    )


def patient_example_form(request, patient_id=None):
    patient = next((item for item in EXAMPLE_PATIENTS if item["id"] == patient_id), None)
    initial = {}
    if patient:
        first_name, _, last_name = patient["name"].partition(" ")
        initial = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": patient["phone"],
            "active": True,
        }
    form = PatientExampleForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        messages.success(
            request,
            "Example form validated successfully. Connect it to your model's save() next.",
        )
        return redirect("patient-examples")
    return render(
        request,
        "pages/form.html",
        {
            "page_title": "Edit patient" if patient else "Add patient",
            "nav_active": "patients",
            "eyebrow": "Reusable form example",
            "page_description": "The same template works with any Django Form or ModelForm.",
            "form": form,
            "submit_label": "Save patient",
            "cancel_url": "/ui/examples/patients/",
        },
    )


def patient_example_detail(request, patient_id):
    patient = next(
        (item for item in EXAMPLE_PATIENTS if item["id"] == patient_id),
        EXAMPLE_PATIENTS[0],
    )
    return render(
        request,
        "pages/detail.html",
        {
            "page_title": patient["name"],
            "nav_active": "patients",
            "eyebrow": "Reusable detail example",
            "fields": [
                {"label": "Full name", "value": patient["name"]},
                {"label": "Phone number", "value": patient["phone"]},
                {"label": "Status", "value": patient["status"]},
            ],
            "back_url": "/ui/examples/patients/",
            "edit_url": f"/ui/examples/patients/{patient['id']}/edit/",
            "delete_url": f"/ui/examples/patients/{patient['id']}/delete/",
        },
    )


def patient_example_delete(request, patient_id):
    if request.method == "POST":
        EXAMPLE_PATIENTS[:] = [item for item in EXAMPLE_PATIENTS if item["id"] != patient_id]
        messages.success(request, "Example patient deleted.")
    return redirect("patient-examples")
