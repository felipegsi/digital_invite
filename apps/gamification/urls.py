from django.urls import path
from apps.gamification import views

app_name = 'gamification'

urlpatterns = [
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("achievements/<uuid:token>/", views.user_achievements, name="user_achievements"),
]
