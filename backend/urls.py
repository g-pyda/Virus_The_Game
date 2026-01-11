from rest_framework.routers import DefaultRouter
from .api import GameViewSet

router = DefaultRouter()
router.register(r"games", GameViewSet, basename="games")

urlpatterns = router.urls
