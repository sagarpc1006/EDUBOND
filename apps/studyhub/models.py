from django.conf import settings
from django.db import models


class StudyMaterial(models.Model):
    TYPE_CHOICES = [("notes", "notes"), ("pyq", "pyq")]

    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="materials")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="notes")
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=120)
    year = models.CharField(max_length=20)
    branch = models.CharField(max_length=20)
    file = models.FileField(upload_to="studyhub/", blank=True, null=True)
    file_type = models.CharField(max_length=10, default="pdf")
    file_size = models.CharField(max_length=20, blank=True, default="")
    downloads = models.PositiveIntegerField(default=0)
    exam_year = models.CharField(max_length=10, blank=True, default="")
    exam_type = models.CharField(max_length=30, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
