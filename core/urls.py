"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from core.cbv_views import (
    LoginShowcaseView,
    LogoutShowcaseView,
    PatientDeleteView,
    PatientDetailView,
    PatientFormView,
    PatientListView,
    SignupShowcaseView,
    VerifyOTPShowcaseView,
)
from core.views import (
    dashboard,
    patient_example_delete,
    patient_example_detail,
    patient_example_form,
    patient_examples,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("ui/examples/patients/", patient_examples, name="patient-examples"),
    path("ui/examples/patients/new/", patient_example_form, name="patient-example-create"),
    path(
        "ui/examples/patients/<int:patient_id>/",
        patient_example_detail,
        name="patient-example-detail",
    ),
    path(
        "ui/examples/patients/<int:patient_id>/edit/",
        patient_example_form,
        name="patient-example-edit",
    ),
    path(
        "ui/examples/patients/<int:patient_id>/delete/",
        patient_example_delete,
        name="patient-example-delete",
    ),
    path(
        "ui/examples-cbv/patients/",
        PatientListView.as_view(),
        name="cbv-patient-list",
    ),
    path(
        "ui/examples-cbv/patients/new/",
        PatientFormView.as_view(),
        name="cbv-patient-create",
    ),
    path(
        "ui/examples-cbv/patients/<int:patient_id>/",
        PatientDetailView.as_view(),
        name="cbv-patient-detail",
    ),
    path(
        "ui/examples-cbv/patients/<int:patient_id>/edit/",
        PatientFormView.as_view(),
        name="cbv-patient-edit",
    ),
    path(
        "ui/examples-cbv/patients/<int:patient_id>/delete/",
        PatientDeleteView.as_view(),
        name="cbv-patient-delete",
    ),
    path(
        "ui/examples-cbv/auth/signup/",
        SignupShowcaseView.as_view(),
        name="cbv-auth-signup",
    ),
    path(
        "ui/examples-cbv/auth/login/",
        LoginShowcaseView.as_view(),
        name="cbv-auth-login",
    ),
    path(
        "ui/examples-cbv/auth/verify-otp/",
        VerifyOTPShowcaseView.as_view(),
        name="cbv-auth-verify-otp",
    ),
    path(
        "ui/examples-cbv/auth/logout/",
        LogoutShowcaseView.as_view(),
        name="cbv-auth-logout",
    ),
    path("admin/", admin.site.urls),
]
