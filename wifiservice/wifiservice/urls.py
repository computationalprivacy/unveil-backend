"""Wifiservice URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('status/', include('status_manager.urls')),
    path('instructions/', include('instructions_manager.urls')),
    path('probe/', include('probe_manager.urls')),
    path('session/', include('session_manager.urls')),
    path('ap/', include('ap_manager.urls')),
    path('display/', include('display_manager.urls')),
    path('django-rq/', include('django_rq.urls')),
    path('access/', include('security_manager.urls'))
]
