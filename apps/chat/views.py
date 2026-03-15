from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User

from .models import ChatConnection, ChatConnectionRequest, ChatMessage, ChatThread
from .serializers import (
    ChatConnectionRequestSerializer,
    ChatConnectionSerializer,
    ChatMessageSerializer,
    ChatThreadSerializer,
)


def _norm(v):
    return (v or "").strip().lower()


def _ordered_pair(a, b):
    x, y = sorted([_norm(a), _norm(b)])
    return x, y


def _is_connected(me_key, other_key):
    k1, k2 = _ordered_pair(me_key, other_key)
    return ChatConnection.objects.filter(key_one=k1, key_two=k2).exists()


class ChatThreadListCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        me_key = _norm(request.query_params.get("me_key"))
        if not me_key:
            return Response([])
        qs = ChatThread.objects.filter(participant_one=me_key) | ChatThread.objects.filter(participant_two=me_key)
        qs = qs.prefetch_related("participants", "messages").order_by("-created_at")
        return Response(ChatThreadSerializer(qs, many=True, context={"request": request}).data)

    def post(self, request):
        me_key = _norm(request.data.get("me_key"))
        other_key = _norm(request.data.get("other_key"))
        me_name = (request.data.get("me_name") or "You").strip()
        other_name = (request.data.get("other_name") or "User").strip()
        subject = request.data.get("subject", "")
        if not me_key or not other_key or me_key == other_key:
            return Response({"error": "Invalid participants"}, status=400)
        p1, p2 = sorted([me_key, other_key])
        thread = ChatThread.objects.filter(participant_one=p1, participant_two=p2).first()
        if not thread:
            thread = ChatThread.objects.create(
                participant_one=p1,
                participant_two=p2,
                participant_one_name=me_name if p1 == me_key else other_name,
                participant_two_name=other_name if p2 == other_key else me_name,
                subject=subject,
            )
        else:
            if p1 == me_key:
                thread.participant_one_name = me_name
                thread.participant_two_name = other_name
            else:
                thread.participant_one_name = other_name
                thread.participant_two_name = me_name
            if subject:
                thread.subject = subject
            thread.save()
        # Optional mapping to real users if email matches
        for key in [me_key, other_key]:
            if "@" in key:
                u = User.objects.filter(email__iexact=key).first()
                if u:
                    thread.participants.add(u)
        return Response(ChatThreadSerializer(thread, context={"request": request}).data, status=201)


class ChatThreadDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, thread_id):
        thread = get_object_or_404(ChatThread, id=thread_id)
        me_key = _norm(request.query_params.get("me_key") or request.data.get("me_key"))
        if me_key not in {thread.participant_one.lower(), thread.participant_two.lower()}:
            raise PermissionDenied("Not part of this thread")
        thread.delete()
        return Response(status=204)


class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.AllowAny]

    def get_thread(self):
        thread = get_object_or_404(ChatThread, id=self.kwargs["thread_id"])
        me_key = _norm(self.request.query_params.get("me_key") or self.request.data.get("me_key"))
        if me_key and me_key not in {thread.participant_one.lower(), thread.participant_two.lower()}:
            raise PermissionDenied("Not part of this thread")
        return thread

    def get_queryset(self):
        return ChatMessage.objects.filter(thread=self.get_thread()).select_related("sender").order_by("created_at")

    def list(self, request, *args, **kwargs):
        thread = self.get_thread()
        me_key = _norm(request.query_params.get("me_key") or request.data.get("me_key"))
        if me_key:
            now = timezone.now()
            ChatMessage.objects.filter(thread=thread).exclude(sender_key__iexact=me_key).filter(delivered_at__isnull=True).update(delivered_at=now)
            ChatMessage.objects.filter(thread=thread).exclude(sender_key__iexact=me_key).filter(read_at__isnull=True).update(read_at=now)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        me_key = _norm(self.request.data.get("me_key"))
        me_name = (self.request.data.get("me_name") or "You").strip()
        sender_user = None
        if "@" in me_key:
            sender_user = User.objects.filter(email__iexact=me_key).first()
        serializer.save(thread=self.get_thread(), sender=sender_user, sender_key=me_key, sender_name=me_name)


class ChatMessageDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def _get_message(self, message_id):
        return get_object_or_404(ChatMessage.objects.select_related("thread"), id=message_id)

    def _assert_participant(self, request, message):
        me_key = _norm(request.query_params.get("me_key") or request.data.get("me_key"))
        if me_key not in {message.thread.participant_one.lower(), message.thread.participant_two.lower()}:
            raise PermissionDenied("Not part of this thread")
        return me_key

    def patch(self, request, message_id):
        message = self._get_message(message_id)
        me_key = self._assert_participant(request, message)
        if me_key != _norm(message.sender_key):
            raise PermissionDenied("Only sender can edit this message")
        content = (request.data.get("content") or "").strip()
        if not content:
            return Response({"error": "Content is required"}, status=400)
        message.content = content
        message.save(update_fields=["content"])
        return Response(ChatMessageSerializer(message).data)

    def delete(self, request, message_id):
        message = self._get_message(message_id)
        me_key = self._assert_participant(request, message)
        if me_key != _norm(message.sender_key):
            raise PermissionDenied("Only sender can delete this message")
        message.delete()
        return Response(status=204)


class ChatConnectionListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        me_key = _norm(request.query_params.get("me_key"))
        if not me_key:
            return Response({"incoming": [], "outgoing": [], "connections": []})

        incoming = ChatConnectionRequest.objects.filter(to_key=me_key, status=ChatConnectionRequest.STATUS_PENDING)
        outgoing = ChatConnectionRequest.objects.filter(from_key=me_key, status=ChatConnectionRequest.STATUS_PENDING)
        connections = ChatConnection.objects.filter(key_one=me_key) | ChatConnection.objects.filter(key_two=me_key)

        return Response(
            {
                "incoming": ChatConnectionRequestSerializer(incoming, many=True).data,
                "outgoing": ChatConnectionRequestSerializer(outgoing, many=True).data,
                "connections": ChatConnectionSerializer(connections, many=True, context={"request": request}).data,
            }
        )


class ChatConnectionRequestCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from_key = _norm(request.data.get("from_key"))
        to_key = _norm(request.data.get("to_key"))
        from_name = (request.data.get("from_name") or "").strip()
        to_name = (request.data.get("to_name") or "").strip()
        reason = (request.data.get("reason") or "").strip()

        if not from_key or not to_key or from_key == to_key:
            return Response({"error": "Invalid users"}, status=400)

        if _is_connected(from_key, to_key):
            return Response({"connected": True, "status": "accepted"})

        existing = (
            ChatConnectionRequest.objects.filter(from_key=from_key, to_key=to_key, status=ChatConnectionRequest.STATUS_PENDING).first()
            or ChatConnectionRequest.objects.filter(from_key=to_key, to_key=from_key, status=ChatConnectionRequest.STATUS_PENDING).first()
        )
        if existing:
            data = ChatConnectionRequestSerializer(existing).data
            data.update({"connected": False, "already_pending": True})
            return Response(data, status=200)

        created = ChatConnectionRequest.objects.create(
            from_key=from_key,
            to_key=to_key,
            from_name=from_name,
            to_name=to_name,
            reason=reason[:255],
            status=ChatConnectionRequest.STATUS_PENDING,
        )
        data = ChatConnectionRequestSerializer(created).data
        data.update({"connected": False})
        return Response(data, status=201)


class ChatConnectionRespondView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, request_id):
        me_key = _norm(request.data.get("me_key"))
        action = _norm(request.data.get("action"))
        if action not in {"accept", "reject"}:
            return Response({"error": "Invalid action"}, status=400)

        req = get_object_or_404(ChatConnectionRequest, id=request_id)
        if req.status != ChatConnectionRequest.STATUS_PENDING:
            return Response({"error": "Request already handled"}, status=400)
        if me_key != _norm(req.to_key):
            raise PermissionDenied("Only recipient can respond")

        req.status = ChatConnectionRequest.STATUS_ACCEPTED if action == "accept" else ChatConnectionRequest.STATUS_REJECTED
        req.responded_at = timezone.now()
        req.save(update_fields=["status", "responded_at"])

        if action == "accept":
            k1, k2 = _ordered_pair(req.from_key, req.to_key)
            n1 = req.from_name if k1 == _norm(req.from_key) else req.to_name
            n2 = req.to_name if k2 == _norm(req.to_key) else req.from_name
            conn, _ = ChatConnection.objects.get_or_create(
                key_one=k1,
                key_two=k2,
                defaults={"key_one_name": n1, "key_two_name": n2},
            )
            if not conn.key_one_name and n1:
                conn.key_one_name = n1
            if not conn.key_two_name and n2:
                conn.key_two_name = n2
            conn.save()

            thread = ChatThread.objects.filter(participant_one=k1, participant_two=k2).first()
            if not thread:
                thread = ChatThread.objects.create(
                    participant_one=k1,
                    participant_two=k2,
                    participant_one_name=conn.key_one_name or n1 or k1,
                    participant_two_name=conn.key_two_name or n2 or k2,
                    subject=req.reason or "",
                )

            return Response({"status": "accepted", "thread_id": thread.id})

        return Response({"status": "rejected"})
