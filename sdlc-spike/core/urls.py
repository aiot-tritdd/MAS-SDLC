from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    TicketViewSet,
    paperclip_status_webhook,
    paperclip_artifact_webhook,
)

router = DefaultRouter()
router.register(r"tickets", TicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("webhooks/paperclip/status/", paperclip_status_webhook),
    path("webhooks/paperclip/artifact/", paperclip_artifact_webhook),
]
