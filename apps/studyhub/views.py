from django.db.models import F
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import StudyMaterial
from .serializers import StudyMaterialSerializer


class StudyMaterialListCreateView(generics.ListCreateAPIView):
    serializer_class = StudyMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = StudyMaterial.objects.select_related("uploader")
        p = self.request.query_params
        if p.get("mine") == "1":
            qs = qs.filter(uploader=self.request.user)
        if p.get("type"):
            qs = qs.filter(type=p["type"])
        if p.get("year"):
            qs = qs.filter(year=p["year"])
        if p.get("branch"):
            qs = qs.filter(branch=p["branch"])
        if p.get("subject"):
            qs = qs.filter(subject__icontains=p["subject"])
        return qs

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)


class StudyMaterialDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = StudyMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyMaterial.objects.select_related("uploader")

    def perform_destroy(self, instance):
        if instance.uploader_id != self.request.user.id:
            raise PermissionDenied("Only uploader can delete this material.")
        instance.delete()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def increment_download(request, material_id):
    updated = StudyMaterial.objects.filter(id=material_id).update(downloads=F("downloads") + 1)
    if not updated:
        return Response({"error": "Material not found"}, status=404)
    item = StudyMaterial.objects.select_related("uploader").get(id=material_id)
    return Response(StudyMaterialSerializer(item).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def subjects(request):
    data = StudyMaterial.objects.values_list("subject", flat=True).distinct().order_by("subject")
    return Response(list(data))
