from django.urls import path

from doctors import views

app_name = "doctors"

urlpatterns = [
    # doctor
    path("", views.DoctorListView.as_view(), name="list"),
    path("<int:pk>/", views.DoctorDetailView.as_view(), name="detail"),
    # specialty
    path("specialties/", views.SpecialtyListView.as_view(), name="specialty-list"),
    path("specialties/create/", views.SpecialtyCreateView.as_view(), name="specialty-create"),
    path("specialties/<int:pk>/edit/", views.SpecialtyUpdateView.as_view(), name="specialty-update"),
    path("specialties/<int:pk>/delete/", views.SpecialtyDeleteView.as_view(), name="specialty-delete"),
]
