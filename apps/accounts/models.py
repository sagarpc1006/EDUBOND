from django.contrib.auth.models import AbstractUser
from django.db import models

YEAR_CHOICES = [
    ("1st Year", "1st Year"),
    ("2nd Year", "2nd Year"),
    ("3rd Year", "3rd Year"),
    ("4th Year", "4th Year"),
    ("Alumni", "Alumni"),
]

BRANCH_CHOICES = [
    ("CSE", "CSE"),
    ("AI & DS", "AI & DS"),
    ("IT", "IT"),
    ("ECE", "ECE"),
    ("EE", "EE"),
    ("ME", "ME"),
    ("CE", "CE"),
    ("CH", "CH"),
]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    college_name = models.CharField(max_length=200, default="Indira ICEM")
    year = models.CharField(max_length=20, choices=YEAR_CHOICES, default="1st Year")
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES, default="CSE")
    bio = models.TextField(blank=True)
    profile_pic = models.FileField(upload_to="avatars/", blank=True, null=True)
    cover_image = models.FileField(upload_to="covers/", blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    connections = models.ManyToManyField("self", symmetrical=True, blank=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.username

    @property
    def connection_count(self):
        return self.connections.count()


class OTPRecord(models.Model):
    PURPOSE_CHOICES = [("login", "login"), ("register", "register")]

    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="login")
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
