from django.urls import path

from .views import HostelDetailView, HostelFAQListCreateView, HostelListView

urlpatterns = [
    path("hostels/", HostelListView.as_view(), name="hostel_list"),
    path("hostels/<slug:slug>/", HostelDetailView.as_view(), name="hostel_detail"),
    path("hostels/<slug:slug>/faqs/", HostelFAQListCreateView.as_view(), name="hostel_faqs"),
]
