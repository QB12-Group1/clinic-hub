from django.urls import path

from doctors import views

app_name = "doctors"

urlpatterns = [path("", views.DoctorListView.as_view(), name="list")]
