from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import TicketViewSet, paperclip_webhook

router = DefaultRouter()
router.register(r"tickets", TicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("webhooks/paperclip/", paperclip_webhook),
]
