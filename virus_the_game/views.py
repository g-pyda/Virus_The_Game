from django.shortcuts import render
from django.urls import path

FRONTEND_DIR = '../frontend/'


def index(request):
    return render(request, FRONTEND_DIR+'index/index.html')


def host_view(request):
    return render(request, FRONTEND_DIR+'gameplay_laptop/index.html')


def player_join_view(request):
    return render(request, FRONTEND_DIR+'join/index.html')


def player_deck_view(request):
    return render(request, FRONTEND_DIR+'gameplay_telephone/index.html')


def player_pl_chc_view(request):
    return render(request, FRONTEND_DIR+'gameplay_telephone/index.html')


def player_cd_chc_view(request):
    return render(request, FRONTEND_DIR+'gameplay_telephone/index.html')


game_urls = [
    path('', index, name='index'),
    path('game/<int:game_id>/', host_view, name='host_view'),
    path('game/join/', player_join_view, name='player_join_view'),
    path('game/<int:game_id>/deck/',
         player_deck_view, name='player_deck_view'),
    path('game/<int:game_id>/pl_chc/',
         player_pl_chc_view, name='player_pl_chc_view'),
    path('game/<int:game_id>/cd_chc/',
         player_cd_chc_view, name='player_cd_chc_view'),
]
