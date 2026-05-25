from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from ninja import NinjaAPI
from apps.reframe.api import router as reframe_router
from apps.face_detection.api import router as face_router

api = NinjaAPI(title="Pixone API", version="0.1.0", urls_namespace="pixone_api")
api.add_router("/reframe", reframe_router)
api.add_router("/face-detection", face_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
