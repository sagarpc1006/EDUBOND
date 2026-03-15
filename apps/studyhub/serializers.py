from rest_framework import serializers

from .models import StudyMaterial


class StudyMaterialSerializer(serializers.ModelSerializer):
    uploader = serializers.CharField(source="uploader.full_name", read_only=True)
    uploader_email = serializers.EmailField(source="uploader.email", read_only=True)
    uploader_init = serializers.SerializerMethodField()
    uploader_avatar = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = [
            "id",
            "uploader",
            "uploader_email",
            "uploader_init",
            "uploader_avatar",
            "type",
            "title",
            "subject",
            "year",
            "branch",
            "file",
            "file_type",
            "file_size",
            "downloads",
            "exam_year",
            "exam_type",
            "created_at",
        ]
        read_only_fields = ["id", "uploader", "downloads", "created_at"]

    def get_uploader_init(self, obj):
        parts = obj.uploader.full_name.split()
        if not parts:
            return "U"
        return "".join([p[0] for p in parts[:2]]).upper()

    def get_uploader_avatar(self, obj):
        if not obj.uploader.profile_pic:
            return ""
        request = self.context.get("request")
        url = obj.uploader.profile_pic.url
        return request.build_absolute_uri(url) if request else url
