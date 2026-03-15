from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Hostel, HostelFAQ
from .serializers import HostelFAQSerializer, HostelSerializer


DEFAULT_HOSTELS = [
    {
        "slug": "boys",
        "title": "Boys' Hostel - Samarth Bhavan",
        "subtitle": "Samarth Bhavan\nBlock A, B & C",
        "selection_badge": "3 Blocks • 180 Rooms",
        "type": "boys",
        "total_capacity": 180,
        "occupied": 42,
        "curfew": "10:30 PM",
        "warden_name": "Mr. Suresh Kumar",
        "warden_init": "SK",
        "warden_phone": "+91 98XXXXXXXX",
        "warden_email": "warden.boys@indiraicem.ac.in",
    },
    {
        "slug": "girls",
        "title": "Girls' Hostel - Savitri Bhavan",
        "subtitle": "Savitri Bhavan\nBlock D & E",
        "selection_badge": "2 Blocks • 120 Rooms",
        "type": "girls",
        "total_capacity": 120,
        "occupied": 68,
        "curfew": "9:30 PM",
        "warden_name": "Mrs. Rekha Sharma",
        "warden_init": "RS",
        "warden_phone": "+91 97XXXXXXXX",
        "warden_email": "warden.girls@indiraicem.ac.in",
    },
]


def ensure_defaults():
    for payload in DEFAULT_HOSTELS:
        Hostel.objects.get_or_create(slug=payload["slug"], defaults=payload)


class HostelListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ensure_defaults()
        return Response(HostelSerializer(Hostel.objects.all(), many=True, context={"request": request}).data)


class HostelDetailView(generics.RetrieveAPIView):
    serializer_class = HostelSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "slug"
    queryset = Hostel.objects.all()

    def get(self, request, *args, **kwargs):
        ensure_defaults()
        return super().get(request, *args, **kwargs)


class HostelFAQListCreateView(generics.ListCreateAPIView):
    serializer_class = HostelFAQSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ensure_defaults()
        return HostelFAQ.objects.filter(hostel__slug=self.kwargs["slug"]).select_related("user", "hostel")

    def perform_create(self, serializer):
        hostel = Hostel.objects.get(slug=self.kwargs["slug"])
        serializer.save(hostel=hostel, user=self.request.user)
