from django.urls import path
from . import views

urlpatterns = [
    path("games/", views.GameCreateView.as_view(), name="game-create"),
    path("games/<int:game_id>/", views.GameDetailView.as_view(), name="game-detail"),
    path("games/<int:game_id>/join/", views.GameJoinView.as_view(), name="game-join"),
]