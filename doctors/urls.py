from django.urls import path

from doctors import views

app_name = "doctors"

urlpatterns = [
    path("", views.DoctorListView.as_view(), name="list"),
    path("<int:pk>/", views.DoctorDetailView.as_view(), name="detail"),
]
