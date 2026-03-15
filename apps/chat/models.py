from django.conf import settings
from django.db import models


class ChatThread(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chat_threads", blank=True)
    participant_one = models.CharField(max_length=255, blank=True, default="", db_index=True)
    participant_two = models.CharField(max_length=255, blank=True, default="", db_index=True)
    participant_one_name = models.CharField(max_length=255, blank=True, default="")
    participant_two_name = models.CharField(max_length=255, blank=True, default="")
    subject = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    sender_key = models.CharField(max_length=255, blank=True, default="", db_index=True)
    sender_name = models.CharField(max_length=255, blank=True, default="")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]


class ChatConnection(models.Model):
    key_one = models.CharField(max_length=255, db_index=True)
    key_two = models.CharField(max_length=255, db_index=True)
    key_one_name = models.CharField(max_length=255, blank=True, default="")
    key_two_name = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["key_one", "key_two"], name="uniq_chat_connection_pair")
        ]


class ChatConnectionRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    from_key = models.CharField(max_length=255, db_index=True)
    to_key = models.CharField(max_length=255, db_index=True)
    from_name = models.CharField(max_length=255, blank=True, default="")
    to_name = models.CharField(max_length=255, blank=True, default="")
    reason = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
