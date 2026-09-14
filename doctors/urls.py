from django.urls import path

from doctors import views

app_name = "doctors"

urlpatterns = [
    path("", views.DoctorListView.as_view(), name="list"),
    path("<int:pk>/", views.DoctorDetailView.as_view(), name="detail"),
    path("create/", views.DoctorCreateView.as_view(), name="create"),
    path("edit/", views.DoctorUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", views.DoctorDeleteView.as_view(), name="delete"),
]
