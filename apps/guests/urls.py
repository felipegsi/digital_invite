from django.urls import path
from apps.guests import views

app_name = 'guests'

urlpatterns = [
    path("create/", views.create_guest, name="create_guest"),
    path("success/<uuid:token>/", views.guest_success, name="guest_success"),
    path("success/", views.guest_success, name="guest_success_default"),
    path("edit/<uuid:token>/", views.edit_guest, name="edit_guest"),
    path("delete/<int:pk>/", views.delete_guest, name="delete_guest"),
    path("detail/<uuid:token>/", views.guest_detail, name="guest_detail"),
]
