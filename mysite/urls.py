"""mysite URL Configuration"""
from django.contrib import admin
from django.urls import include, path
urlpatterns = [
    path('puzzle/', include('puzzle.urls')),
]
