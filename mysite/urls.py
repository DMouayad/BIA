"""mysite URL Configuration"""
from django.urls import include, path

urlpatterns = [
    path("bia/", include("bia.urls")),
]
