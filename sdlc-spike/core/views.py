from django.shortcuts import render
from core.models import Ticket
from core.serializers import TicketSerializer
from rest_framework import viewsets


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by("-created_at")
    serializer_class = TicketSerializer


# Create your views here.
