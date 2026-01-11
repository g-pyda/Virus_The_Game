from django.urls import path
from rest_framework.routers import DefaultRouter
from .api import GameViewSet, PlayerViewSet

router = DefaultRouter()
router.register(r"games", GameViewSet, basename="games")
router.register(r"players", PlayerViewSet, basename="players")

# Map guideline-required methods to /api/games/{game_id}/
game_detail = GameViewSet.as_view({
    "post": "join",            # POST /api/games/{id}/
    "delete": "remove_player", # DELETE /api/games/{id}/
    "patch": "finish",         # PATCH /api/games/{id}/
})

urlpatterns = [
    path("games/<int:pk>/", game_detail),
] + router.urls