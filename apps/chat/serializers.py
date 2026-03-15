from rest_framework import serializers

from .models import ChatConnection, ChatConnectionRequest, ChatMessage, ChatThread


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_display = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "thread",
            "sender",
            "sender_key",
            "sender_name",
            "sender_display",
            "content",
            "created_at",
            "delivered_at",
            "read_at",
        ]
        read_only_fields = ["id", "thread", "sender", "created_at"]

    def get_sender_display(self, obj):
        if obj.sender_name:
            return obj.sender_name
        if obj.sender:
            return obj.sender.full_name
        return "User"


class ChatThreadSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    other_name = serializers.SerializerMethodField()
    other_key = serializers.SerializerMethodField()

    class Meta:
        model = ChatThread
        fields = [
            "id",
            "participants",
            "participant_one",
            "participant_two",
            "participant_one_name",
            "participant_two_name",
            "other_name",
            "other_key",
            "subject",
            "last_message",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        if not last:
            return None
        return ChatMessageSerializer(last).data

    def _me(self):
        request = self.context.get("request")
        if not request:
            return ""
        return (request.query_params.get("me_key") or request.data.get("me_key") or "").strip().lower()

    def get_other_name(self, obj):
        me = self._me()
        if not me:
            return obj.participant_two_name or obj.participant_one_name
        if obj.participant_one.lower() == me:
            return obj.participant_two_name
        return obj.participant_one_name

    def get_other_key(self, obj):
        me = self._me()
        if not me:
            return obj.participant_two or obj.participant_one
        if obj.participant_one.lower() == me:
            return obj.participant_two
        return obj.participant_one


class ChatConnectionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatConnectionRequest
        fields = [
            "id",
            "from_key",
            "to_key",
            "from_name",
            "to_name",
            "reason",
            "status",
            "created_at",
            "responded_at",
        ]
        read_only_fields = ["id", "status", "created_at", "responded_at"]


class ChatConnectionSerializer(serializers.ModelSerializer):
    other_key = serializers.SerializerMethodField()
    other_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatConnection
        fields = [
            "id",
            "key_one",
            "key_two",
            "key_one_name",
            "key_two_name",
            "other_key",
            "other_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def _me(self):
        request = self.context.get("request")
        if not request:
            return ""
        return (request.query_params.get("me_key") or request.data.get("me_key") or "").strip().lower()

    def get_other_key(self, obj):
        me = self._me()
        if not me:
            return obj.key_two
        if obj.key_one.lower() == me:
            return obj.key_two
        return obj.key_one

    def get_other_name(self, obj):
        me = self._me()
        if not me:
            return obj.key_two_name or obj.key_two
        if obj.key_one.lower() == me:
            return obj.key_two_name or obj.key_two
        return obj.key_one_name or obj.key_one
