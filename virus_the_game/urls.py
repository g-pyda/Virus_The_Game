"""
URL configuration for virus_game_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

from .views import game_urls

# Serve scripts and other frontend assets
def serve_frontend_file(request, path):
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
    
    return serve(request, path, document_root=frontend_dir)


urlpatterns = [
    path("admin/", admin.site.urls),

    # Your REST API (DRF)
    path("api/", include("backend.urls")),

    # Game routes (from game_urls) - these take priority
    path("", include(game_urls)),

    # Serve frontend static assets (scripts, styles, etc.) - catch-all at the end
    path("<path:path>", serve_frontend_file),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
