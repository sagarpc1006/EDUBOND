from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Listing, ListingImage
from .serializers import ListingImageSerializer, ListingSerializer


class ListingListCreateView(generics.ListCreateAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Listing.objects.filter(is_active=True).select_related("owner").prefetch_related("images")
        category = self.request.query_params.get("category")
        q = self.request.query_params.get("q")
        mine = self.request.query_params.get("mine")
        if category and category != "all":
            qs = qs.filter(category=category)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if mine == "1":
            if not self.request.user.is_authenticated:
                return Listing.objects.none()
            qs = qs.filter(owner=self.request.user)
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        payload = {}
        if user:
            payload["owner"] = user
            payload["seller"] = user.full_name
            payload["seller_init"] = "".join([p[0] for p in user.full_name.split()[:2]]).upper() or "U"
            payload["branch"] = user.branch
        else:
            payload["seller"] = self.request.data.get("seller", "Student")
            payload["seller_init"] = self.request.data.get("seller_init", "ST")
            payload["branch"] = self.request.data.get("branch", "")
        serializer.save(**payload)


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Listing.objects.select_related("owner").prefetch_related("images")

    def perform_update(self, serializer):
        listing = self.get_object()
        if listing.owner_id != getattr(self.request.user, "id", None):
            raise PermissionDenied("You can update only your own listing.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner_id != getattr(self.request.user, "id", None):
            raise PermissionDenied("You can delete only your own listing.")
        instance.delete()


class ListingImageCreateView(generics.CreateAPIView):
    serializer_class = ListingImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        listing_id = self.kwargs["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        if listing.owner_id and listing.owner_id != getattr(self.request.user, "id", None):
            raise PermissionDenied("You can add images only to your own listing.")
        serializer.save(listing=listing)
