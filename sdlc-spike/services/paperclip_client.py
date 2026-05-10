import os
import requests
from core.models import Ticket

class PaperclipClient:
    def __init__(self):
        self.base_url = os.getenv('PAPERCLIP_API_URL', 'http://localhost:3100/api')
        self.company_id = os.getenv('PAPERCLIP_COMPANY_ID')

    def sync_ticket(self, ticket: Ticket) -> dict:
        url = f"{self.base_url}/companies/{self.company_id}/issues"
        payload = {
            'title': ticket.title,
            'description': ticket.description,
            'priority': ticket.priority,
            'external_id': str(ticket.id),
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        ticket.paperclip_issue_id = data['id']
        ticket.save(update_fields=['paperclip_issue_id'])
        return data
        
