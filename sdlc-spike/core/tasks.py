from celery import shared_task
from core.models import Ticket
from services.paperclip_client import PaperclipClient

@shared_task
def sync_ticket_to_paperclip(ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    client = PaperclipClient()
    client.sync_ticket(ticket)
