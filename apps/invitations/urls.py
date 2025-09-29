from django.urls import path
from apps.invitations import views

app_name = 'invitations'

urlpatterns = [
    path("create/", views.create_invite, name="create_invite"),
    path("detail/<uuid:token>/", views.invite_detail, name="invite_detail"),
    path("detail/<uuid:token>/complete_profile/", views.complete_profile, name="complete_profile"),
    path("respond/<uuid:token>/", views.respond_invite, name="respond_invite"),
]
