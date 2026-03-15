from django.contrib import admin

from .models import Hostel, HostelFAQ


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title",
        "subtitle",
        "type",
        "total_capacity",
        "occupied",
        "curfew",
        "warden_name",
        "warden_phone",
    )
    list_editable = ("total_capacity", "occupied", "curfew", "warden_phone")
    search_fields = ("slug", "title", "warden_name", "warden_email")
    list_filter = ("type",)
    fieldsets = (
        ("Hostel Info", {
            "fields": ("slug", "title", "subtitle", "selection_badge", "type", "cover_photo")
        }),
        ("Capacity", {
            "fields": ("total_capacity", "occupied", "curfew")
        }),
        ("Warden", {
            "fields": ("warden_name", "warden_init", "warden_photo", "warden_phone", "warden_email")
        }),
    )


@admin.register(HostelFAQ)
class HostelFAQAdmin(admin.ModelAdmin):
    list_display = ("hostel", "question", "user", "created_at")
    search_fields = ("question", "answer", "hostel__title", "user__email")
    list_filter = ("hostel", "created_at")
