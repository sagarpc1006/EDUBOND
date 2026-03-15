from django.contrib import admin

from .models import ChatMessage, ChatThread

admin.site.register(ChatThread)
admin.site.register(ChatMessage)
