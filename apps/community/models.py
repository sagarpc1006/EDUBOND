from django.conf import settings
from django.db import models


class Post(models.Model):
    TAG_CHOICES = [
        ("general", "general"),
        ("roadmap", "roadmap"),
        ("event", "event"),
        ("experience", "experience"),
        ("tip", "tip"),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default="general")
    content = models.TextField()
    event_date = models.DateField(null=True, blank=True)
    event_logo = models.CharField(max_length=20, blank=True, default="")
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class Grievance(models.Model):
    CATEGORY_CHOICES = [
        ("Academic Issue", "Academic Issue"),
        ("Hostel Problem", "Hostel Problem"),
        ("Faculty Complaint", "Faculty Complaint"),
        ("Infrastructure", "Infrastructure"),
        ("Other", "Other"),
    ]
    STATUS_CHOICES = [("open", "open"), ("reviewing", "reviewing"), ("resolved", "resolved")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
