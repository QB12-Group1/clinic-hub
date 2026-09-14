from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("", views.PatientListView.as_view(), name="list"),
    path("create/", views.PatientCreateView.as_view(), name="create"),
    path("<int:pk>/", views.PatientDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.PatientEditView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.PatientDeleteView.as_view(), name="delete"),
    path("home/", views.PatientHomeView.as_view(), name="home"),
]
