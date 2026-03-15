from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    connection_count = serializers.ReadOnlyField()
    profile_pic = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "name",
            "username",
            "college_name",
            "year",
            "branch",
            "bio",
            "profile_pic",
            "cover_image",
            "skills",
            "connection_count",
            "is_email_verified",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = ["id", "email", "is_email_verified", "is_staff", "is_superuser"]

    def get_name(self, obj):
        return obj.full_name

    def _absolute_file_url(self, file_obj):
        if not file_obj:
            return ""
        request = self.context.get("request")
        url = file_obj.url
        return request.build_absolute_uri(url) if request else url

    def get_profile_pic(self, obj):
        return self._absolute_file_url(obj.profile_pic)

    def get_cover_image(self, obj):
        return self._absolute_file_url(obj.cover_image)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "name", "year", "branch", "password"]

    def validate_email(self, value):
        if not value.endswith("@indiraicem.ac.in"):
            raise serializers.ValidationError("Only @indiraicem.ac.in emails are allowed.")
        return value.lower()

    def create(self, validated_data):
        name = validated_data.pop("name").strip()
        password = validated_data.pop("password")
        first_name, _, last_name = name.partition(" ")
        user = User(
            **validated_data,
            username=validated_data["email"].split("@")[0],
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        return user
