import logging
import random
import string
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPRecord, User
from .serializers import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)


def _generate_otp():
    return "".join(random.choices(string.digits, k=6))


def _log_dev_otp(email, purpose, otp, note=""):
    msg = f"DEV OTP for {email} ({purpose}): {otp} {note}".strip()
    print(msg, flush=True)
    logger.warning(msg)
    try:
        tmp_dir = Path(getattr(settings, "BASE_DIR", Path("."))) / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        with (tmp_dir / "dev_otp.log").open("a", encoding="utf-8") as fh:
            fh.write(msg + "\n")
    except Exception:
        pass


def _valid_otp(email, otp, purpose):
    return OTPRecord.objects.filter(
        email=email,
        otp=otp,
        purpose=purpose,
        is_used=False,
        created_at__gte=timezone.now() - timedelta(minutes=10),
    ).first()


@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    """OTP disabled: always return a static code for compatibility."""
    email = request.data.get("email", "").strip().lower()
    purpose = request.data.get("purpose", "login").strip().lower()
    if purpose not in {"login", "register"}:
        return Response({"error": "Invalid purpose"}, status=400)
    if not email.endswith("@indiraicem.ac.in"):
        return Response({"error": "Only @indiraicem.ac.in emails allowed."}, status=400)
    static_otp = "000000"
    _log_dev_otp(email, purpose, static_otp, "(OTP disabled; static code)")
    return Response({"message": f"OTP disabled; use code {static_otp}", "dev_otp": static_otp})


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "No account with this email. Please register."}, status=404)
    if not user.check_password(password):
        return Response({"error": "Incorrect password"}, status=400)

    # Mark any outstanding OTPs as used, but do not block.
    OTPRecord.objects.filter(email=email, purpose="login", is_used=False).update(is_used=True)

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get("email", "").strip().lower()
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already registered. Please login."}, status=400)

    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])

    OTPRecord.objects.filter(email=email, purpose="register", is_used=False).update(is_used=True)

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    if request.method == "GET":
        return Response(UserSerializer(user, context={"request": request}).data)

    name = request.data.get("name")
    if name is not None:
        first_name, _, last_name = name.strip().partition(" ")
        user.first_name = first_name
        user.last_name = last_name
    for field in ["bio", "year", "branch", "skills"]:
        if field in request.data:
            setattr(user, field, request.data[field])
    if "profile_pic" in request.FILES:
        user.profile_pic = request.FILES["profile_pic"]
    if "cover_image" in request.FILES:
        user.cover_image = request.FILES["cover_image"]
    user.save()
    return Response(UserSerializer(user, context={"request": request}).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def people_list(request):
    qs = User.objects.exclude(id=request.user.id)
    q = request.GET.get("q", "").strip()
    year = request.GET.get("year", "").strip()
    branch = request.GET.get("branch", "").strip()
    if q:
        qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))
    if year:
        qs = qs.filter(year=year)
    if branch:
        qs = qs.filter(branch=branch)
    return Response(UserSerializer(qs[:20], many=True, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def connect(request, user_id):
    try:
        other = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    request.user.connections.add(other)
    return Response({"message": f"Connected with {other.full_name}"})
