import importlib.util

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve


def health(_request):
    return JsonResponse({"status": "ok", "service": "edubond-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("home.html", TemplateView.as_view(template_name="home.html"), name="home"),
    path("marketplace.html", TemplateView.as_view(template_name="marketplace.html"), name="marketplace"),
    path("studyhub.html", TemplateView.as_view(template_name="studyhub.html"), name="studyhub"),
    path("hostel.html", TemplateView.as_view(template_name="hostel.html"), name="hostel"),
    path("profile.html", TemplateView.as_view(template_name="profile.html"), name="profile"),
    path("messages.html", TemplateView.as_view(template_name="messages.html"), name="messages"),
    path("health/", health),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Dev-only helper to serve local css/js/html files from BASE_DIR.
if settings.DEBUG:
    urlpatterns += [
        re_path(r"^(?P<path>.*\.(css|js|html))$", serve, {"document_root": settings.BASE_DIR}),
    ]

if importlib.util.find_spec("rest_framework"):
    urlpatterns += [
        path("api/community/", include("apps.community.urls")),
        path("api/marketplace/", include("apps.marketplace.urls")),
        path("api/studyhub/", include("apps.studyhub.urls")),
        path("api/hostel/", include("apps.hostel.urls")),
        path("api/chat/", include("apps.chat.urls")),
    ]

if importlib.util.find_spec("rest_framework") and importlib.util.find_spec("rest_framework_simplejwt"):
    urlpatterns += [path("api/auth/", include("apps.accounts.urls"))]
