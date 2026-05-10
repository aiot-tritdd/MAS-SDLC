from unittest.mock import patch
from django.test import TestCase
from core.models import Ticket
from services.paperclip_client import PaperclipClient

class PaperClipClientTest(TestCase):
    @patch('services.paperclip_client.requests.post')
    def test_sync_ticket_creates_paperclip_issues(self, mock_post):
        # ~ Mimic what the Paperclip API returns when creating an issue
        mock_post.return_value.json.return_value = {"id": "pp-issues-123"}
        mock_post.return_value.status_code = 201

        ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Desc",
            status=Ticket.Status.NEW,
            priority=Ticket.Priority.MEDIUM,
        )
        # ~ Instantiate the client
        client = PaperclipClient()
        # ~ Run the method under test
        result = client.sync_ticket(ticket)

        self.assertEqual(result['id'], 'pp-issues-123')
        ticket.refresh_from_db()
        self.assertEqual(Ticket.objects.last().paperclip_issue_id, 'pp-issues-123')

    @patch('services.paperclip_client.requests.post')
    def test_sync_ticket_calls_correct_endpoint(self, mock_post):
        mock_post.return_value.json.return_value = {'id': 'pc-123'}
        mock_post.return_value.status_code = 201

        ticket = Ticket.objects.create(title="Test", description="Desc")
        client = PaperclipClient()
        client.sync_ticket(ticket)

        call_url = mock_post.call_args[0][0]
        self.assertIn('/issues', call_url)

    @patch('services.paperclip_client.requests.post')
    def test_sync_ticket_raises_on_api_error(self, mock_post):
        mock_post.side_effect = Exception("Paperclip connection refused")
        ticket = Ticket.objects.create(title="Test", description="Desc")
        client = PaperclipClient()

        with self.assertRaises(Exception):
            client.sync_ticket(ticket)
