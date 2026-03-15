from rest_framework import serializers

from .models import Listing, ListingImage


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ["id", "image"]
        read_only_fields = ["id"]


class ListingSerializer(serializers.ModelSerializer):
    seller_name = serializers.SerializerMethodField()
    seller_initials = serializers.SerializerMethodField()
    seller_branch = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    images = ListingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id",
            "owner",
            "seller",
            "seller_init",
            "branch",
            "seller_name",
            "seller_initials",
            "seller_branch",
            "is_owner",
            "name",
            "category",
            "price",
            "description",
            "contact",
            "condition",
            "photo",
            "is_active",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at", "seller_name", "seller_initials", "seller_branch"]

    def get_seller_name(self, obj):
        if obj.owner:
            return obj.owner.full_name
        return obj.seller

    def get_seller_initials(self, obj):
        if obj.owner:
            parts = obj.owner.full_name.split()
        else:
            parts = obj.seller.split()
        if not parts:
            return "U"
        return "".join([p[0] for p in parts[:2]]).upper()

    def get_seller_branch(self, obj):
        if obj.owner:
            return obj.owner.branch
        return obj.branch

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.owner_id == request.user.id
