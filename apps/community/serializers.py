from rest_framework import serializers

from .models import Grievance, Post, PostComment


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_email = serializers.EmailField(source="author.email", read_only=True)
    author_avatar = serializers.SerializerMethodField()
    author_initials = serializers.SerializerMethodField()
    sub = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(source="likes.count", read_only=True)
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_name",
            "author_email",
            "author_avatar",
            "author_initials",
            "sub",
            "tag",
            "content",
            "event_date",
            "event_logo",
            "like_count",
            "comment_count",
            "liked",
            "created_at",
        ]
        read_only_fields = ["id", "author", "created_at"]

    def get_author_avatar(self, obj):
        if not obj.author.profile_pic:
            return ""
        request = self.context.get("request")
        url = obj.author.profile_pic.url
        return request.build_absolute_uri(url) if request else url

    def get_author_initials(self, obj):
        parts = obj.author.full_name.split()
        if not parts:
            return "U"
        return "".join([p[0] for p in parts[:2]]).upper()

    def get_sub(self, obj):
        return f"{obj.author.year} • {obj.author.branch}"

    def get_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(id=request.user.id).exists()


class PostCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = PostComment
        fields = ["id", "post", "author", "author_name", "author_email", "content", "created_at"]
        read_only_fields = ["id", "post", "author", "created_at"]


class GrievanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grievance
        fields = [
            "id",
            "user",
            "category",
            "subject",
            "description",
            "is_anonymous",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "user", "status", "created_at"]
