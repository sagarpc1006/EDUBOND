from django.urls import path

from .views import (
    GrievanceListCreateView,
    PostCommentListCreateView,
    PostListCreateView,
    community_events,
    delete_post,
    people_suggestions,
    toggle_post_like,
)

urlpatterns = [
    path("posts/", PostListCreateView.as_view(), name="posts"),
    path("posts/<int:post_id>/", delete_post, name="post_delete"),
    path("posts/<int:post_id>/like/", toggle_post_like, name="post_like"),
    path("posts/<int:post_id>/comments/", PostCommentListCreateView.as_view(), name="post_comments"),
    path("grievances/", GrievanceListCreateView.as_view(), name="grievances"),
    path("suggestions/", people_suggestions, name="people_suggestions"),
    path("events/", community_events, name="community_events"),
]
