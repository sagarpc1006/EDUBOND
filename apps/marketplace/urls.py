from django.urls import path

from .views import ListingDetailView, ListingImageCreateView, ListingListCreateView

urlpatterns = [
    path("listings/", ListingListCreateView.as_view(), name="listing_list_create"),
    path("listings/<int:pk>/", ListingDetailView.as_view(), name="listing_detail"),
    path("listings/<int:listing_id>/images/", ListingImageCreateView.as_view(), name="listing_image_create"),
]
