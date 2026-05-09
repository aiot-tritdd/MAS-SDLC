from rest_framework import serializers
from core.models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at', 'paperclip_issue_id']
        read_only_fields = ['id', 'created_at', 'updated_at', 'paperclip_issue_id']
