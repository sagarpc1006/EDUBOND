from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.serializers import UserSerializer

from .models import Grievance, Post, PostComment
from .serializers import GrievanceSerializer, PostCommentSerializer, PostSerializer


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Post.objects.select_related("author").prefetch_related("likes", "comments")
        tag = self.request.query_params.get("tag")
        mine = self.request.query_params.get("mine")
        if tag and tag != "all":
            qs = qs.filter(tag=tag)
        if mine == "1":
            if not self.request.user.is_authenticated:
                return Post.objects.none()
            qs = qs.filter(author=self.request.user)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def toggle_post_like(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=404)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return Response({"liked": liked, "like_count": post.likes.count()})


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=404)
    if post.author_id != request.user.id and not request.user.is_staff and not request.user.is_superuser:
        return Response({"error": "Only author or admin can delete this post"}, status=403)
    post.delete()
    return Response(status=204)


class PostCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PostComment.objects.filter(post_id=self.kwargs["post_id"]).select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_id=self.kwargs["post_id"])


class GrievanceListCreateView(generics.ListCreateAPIView):
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Grievance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def people_suggestions(request):
    people = (
        request.user.__class__.objects.exclude(id=request.user.id)
        .order_by("-date_joined")
        .select_related()[:8]
    )
    return Response(UserSerializer(people, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def community_events(_request):
    events = [
        {"title": "Tech Fest 2025", "date": "2025-03-15", "place": "Main Auditorium", "time": "10:00"},
        {"title": "Hackathon 2025", "date": "2025-03-20", "place": "Computer Lab", "time": "09:00"},
        {"title": "Alumni Meet", "date": "2025-03-28", "place": "Seminar Hall", "time": "14:00"},
        {"title": "Cultural Night", "date": "2025-04-05", "place": "Open Ground", "time": "18:00"},
    ]
    return Response(events, status=status.HTTP_200_OK)
