from core.models import Ticket
from core.serializers import TicketSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by("-created_at")
    serializer_class = TicketSerializer

@api_view(["POST"])
def paperclip_webhook(request):
    data = request.data
    issue_id = data.get("issue_id")
    new_status = data.get("status")
    ticket = get_object_or_404(Ticket, paperclip_issue_id=issue_id)
    ticket.status = new_status
    ticket.save(update_fields=["status"])
    return Response({"status": "success"}, status=200)

# Create your views here.
