from django.contrib import admin

from .models import Grievance, Post, PostComment

admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(Grievance)
