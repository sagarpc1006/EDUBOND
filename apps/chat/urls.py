from django.urls import path

from .views import (
    ChatConnectionListView,
    ChatConnectionRequestCreateView,
    ChatConnectionRespondView,
    ChatMessageDetailView,
    ChatMessageListCreateView,
    ChatThreadDetailView,
    ChatThreadListCreateView,
)

urlpatterns = [
    path("threads/", ChatThreadListCreateView.as_view(), name="chat_threads"),
    path("threads/<int:thread_id>/", ChatThreadDetailView.as_view(), name="chat_thread_detail"),
    path("threads/<int:thread_id>/messages/", ChatMessageListCreateView.as_view(), name="chat_messages"),
    path("messages/<int:message_id>/", ChatMessageDetailView.as_view(), name="chat_message_detail"),
    path("connections/", ChatConnectionListView.as_view(), name="chat_connections"),
    path("connections/request/", ChatConnectionRequestCreateView.as_view(), name="chat_connection_request"),
    path("connections/<int:request_id>/respond/", ChatConnectionRespondView.as_view(), name="chat_connection_respond"),
]
