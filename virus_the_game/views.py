from django.shortcuts import render
from django.urls import path
from django.http import FileResponse
import os

# Get the app directory (/app/virus_the_game/)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root (/app/)
PROJECT_ROOT = os.path.dirname(APP_DIR)
# Frontend directory is at /app/frontend/
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')


def serve_html(filepath):
    """Helper to serve HTML files with proper error handling"""
    def view(request, **kwargs):
        full_path = os.path.join(FRONTEND_DIR, filepath)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return render(request, filepath)
        from django.http import HttpResponse
        return HttpResponse(f"File not found: {filepath}", status=404)
    return view


def index(request):
    full_path = os.path.join(FRONTEND_DIR, 'home/index.html')
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            from django.http import HttpResponse
            return HttpResponse(f.read(), content_type='text/html')
    from django.http import HttpResponse
    return HttpResponse(f"Template not found: {full_path}", status=404)


def host_view(request, game_id):
    full_path = os.path.join(FRONTEND_DIR, 'gameplay_laptop/index.html')
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            from django.http import HttpResponse
            return HttpResponse(f.read(), content_type='text/html')
    from django.http import HttpResponse
    return HttpResponse(f"Template not found: {full_path}", status=404)


def player_join_view(request):
    full_path = os.path.join(FRONTEND_DIR, 'gameplay_join/index.html')
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            from django.http import HttpResponse
            return HttpResponse(f.read(), content_type='text/html')
    from django.http import HttpResponse
    return HttpResponse(f"Template not found: {full_path}", status=404)


def player_deck_view(request, game_id):
    full_path = os.path.join(FRONTEND_DIR, 'gameplay_telephone/player_deck/deck.html')
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            from django.http import HttpResponse
            return HttpResponse(f.read(), content_type='text/html')
    from django.http import HttpResponse
    return HttpResponse(f"Template not found: {full_path}", status=404)


def player_pl_chc_view(request, game_id):
    full_path = os.path.join(FRONTEND_DIR, 'gameplay_telephone/index.html')
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            from django.http import HttpResponse
            return HttpResponse(f.read(), content_type='text/html')
    from django.http import HttpResponse
    return HttpResponse(f"Template not found: {full_path}", status=404)


def player_cd_chc_view(request, game_id):
    full_path = os.path.join(FRONTEND_DIR, 'gameplay_telephone/index.html')
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            from django.http import HttpResponse
            return HttpResponse(f.read(), content_type='text/html')
    from django.http import HttpResponse
    return HttpResponse(f"Template not found: {full_path}", status=404)


def leaderboard_view(request):
    full_path = os.path.join(FRONTEND_DIR, 'leaderboard/leaderboard.html')
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            from django.http import HttpResponse
            return HttpResponse(f.read(), content_type='text/html')
    from django.http import HttpResponse
    return HttpResponse(f"Template not found: {full_path}", status=404)


game_urls = [
    path('', index, name='index'),
    path('home/', index, name='home'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('game/<int:game_id>/', host_view, name='host_view'),
    path('game/join/', player_join_view, name='player_join_view'),
    path('game/<int:game_id>/deck/',
         player_deck_view, name='player_deck_view'),
    path('game/<int:game_id>/pl_chc/',
         player_pl_chc_view, name='player_pl_chc_view'),
    path('game/<int:game_id>/cd_chc/',
         player_cd_chc_view, name='player_cd_chc_view'),
]
