from django.conf import settings
from django.db import models


class Listing(models.Model):
    CATEGORY_CHOICES = [
        ("calculator", "calculator"),
        ("books", "books"),
        ("stationery", "stationery"),
        ("electronics", "electronics"),
        ("notes", "notes"),
        ("other", "other"),
    ]
    CONDITION_CHOICES = [("Like New", "Like New"), ("Good", "Good"), ("Used", "Used")]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
        null=True,
        blank=True,
    )
    seller = models.CharField(max_length=120, blank=True, default="")
    seller_init = models.CharField(max_length=4, blank=True, default="")
    branch = models.CharField(max_length=20, blank=True, default="")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    price = models.PositiveIntegerField()
    description = models.TextField()
    contact = models.CharField(max_length=200)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="Like New")
    photo = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="marketplace/")
