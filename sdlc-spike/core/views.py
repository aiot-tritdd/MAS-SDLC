from core.models import Ticket
from core.serializers import TicketSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.tasks import sync_ticket_to_paperclip, notify_telegram


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by("-created_at")
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        ticket = serializer.save()
        sync_ticket_to_paperclip.delay(str(ticket.id))


@api_view(["POST"])
def paperclip_webhook(request):
    # Webhooks calleds our endpoints and we would update our status with whatever Paperclip give us
    data = request.data
    issue_id = data.get("issue_id")
    new_status = data.get("status")
    ticket = get_object_or_404(Ticket, paperclip_issue_id=issue_id)
    ticket.status = new_status
    ticket.save(update_fields=["status"])

    # Update webhooks so when the Paperclips needs approval it can send telegram message for us
    if new_status == "needs_approval":
        notify_telegram.delay(str(ticket.id))
    return Response({"status": "success"}, status=200)

# Create your views here.
