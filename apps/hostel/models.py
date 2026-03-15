from django.conf import settings
from django.db import models


class Hostel(models.Model):
    TYPE_CHOICES = [("boys", "boys"), ("girls", "girls")]

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, default="")
    selection_badge = models.CharField(max_length=80, blank=True, default="")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    cover_photo = models.FileField(upload_to="hostels/", blank=True, null=True)
    total_capacity = models.PositiveIntegerField()
    occupied = models.PositiveIntegerField()
    curfew = models.CharField(max_length=30)
    warden_name = models.CharField(max_length=120)
    warden_init = models.CharField(max_length=4)
    warden_photo = models.FileField(upload_to="wardens/", blank=True, null=True)
    warden_phone = models.CharField(max_length=40)
    warden_email = models.EmailField()

    def __str__(self):
        return self.title


class HostelFAQ(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="faqs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
