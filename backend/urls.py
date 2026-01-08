from django.urls import path
from .views import game_index


urlpatterns = [
    path('', game_index)
]

