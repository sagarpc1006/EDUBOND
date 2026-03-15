from rest_framework import serializers

from .models import Hostel, HostelFAQ


class HostelSerializer(serializers.ModelSerializer):
    vacancy = serializers.SerializerMethodField()
    vacancy_percent = serializers.SerializerMethodField()
    cover_photo_url = serializers.SerializerMethodField()
    warden_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Hostel
        fields = [
            "id",
            "slug",
            "title",
            "subtitle",
            "selection_badge",
            "type",
            "cover_photo_url",
            "total_capacity",
            "occupied",
            "vacancy",
            "vacancy_percent",
            "curfew",
            "warden_name",
            "warden_init",
            "warden_photo_url",
            "warden_phone",
            "warden_email",
        ]

    def get_vacancy(self, obj):
        return max(obj.total_capacity - obj.occupied, 0)

    def get_vacancy_percent(self, obj):
        if obj.total_capacity == 0:
            return 0
        return round((obj.occupied / obj.total_capacity) * 100)

    def _absolute_file_url(self, file_obj):
        if not file_obj:
            return ""
        request = self.context.get("request")
        url = file_obj.url
        return request.build_absolute_uri(url) if request else url

    def get_cover_photo_url(self, obj):
        return self._absolute_file_url(obj.cover_photo)

    def get_warden_photo_url(self, obj):
        return self._absolute_file_url(obj.warden_photo)


class HostelFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelFAQ
        fields = ["id", "hostel", "user", "question", "answer", "created_at"]
        read_only_fields = ["id", "hostel", "user", "created_at"]
