from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "download_all_solutions",
        views.downloadAllSolutions,
        name="download_all_solutions",
    ),
    path(
        "download_optimal_solutions",
        views.downloadOptimalSolutionsFile,
        name="download_optimal_solutions",
    ),
]
