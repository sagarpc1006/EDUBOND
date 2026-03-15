from django.urls import path

from .views import StudyMaterialDetailView, StudyMaterialListCreateView, increment_download, subjects

urlpatterns = [
    path("materials/", StudyMaterialListCreateView.as_view(), name="materials"),
    path("materials/<int:pk>/", StudyMaterialDetailView.as_view(), name="material_detail"),
    path("materials/<int:material_id>/download/", increment_download, name="material_download"),
    path("subjects/", subjects, name="subjects"),
]
