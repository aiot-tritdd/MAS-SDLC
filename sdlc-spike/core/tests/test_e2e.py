from django.test import TestCase
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from core.models import Ticket, Artifact, AgentRun
from services.paperclip_client import PaperclipClient
class SpikeEndToEndTest(TestCase):
    """
    Tests the full spike pipeline with mocked external services.
    Validates: create ticket → sync → artifact → status change → Telegram notification.
    """

    @patch('core.tasks.notify_telegram.delay')
    @patch('core.tasks.sync_ticket_to_paperclip.delay')
    @patch('services.paperclip_client.requests.post')
    def test_full_spike_pipeline(self, mock_paperclip_post, mock_sync_delay, mock_notify_delay):
        api = APIClient()

        # 1. Create ticket via API
        mock_paperclip_post.return_value.json.return_value = {'id': 'pc-e2e-999'}
        mock_paperclip_post.return_value.status_code = 201

        create_response = api.post('/api/tickets/', {
            'title': 'Add user authentication endpoint',
            'description': 'Create JWT auth with DRF. Include rate limiting.',
        }, format='json')
        self.assertEqual(create_response.status_code, 201)
        ticket_id = create_response.data['id']

        # 2. Sync ticket to Paperclip manually
        ticket = Ticket.objects.get(id=ticket_id)
        client = PaperclipClient()
        client.sync_ticket(ticket)
        ticket.refresh_from_db()
        self.assertEqual(ticket.paperclip_issue_id, 'pc-e2e-999')

        # 3. Paperclip fires artifact webhook (research complete)
        artifact_response = api.post('/api/webhooks/paperclip/artifact/', {
            'issue_id': 'pc-e2e-999',
            'artifact_type': 'research',
            'title': 'auth-research.md',
            'content': '## Auth Research\n\nRecommend JWT with djangorestframework-simplejwt...',
            'agent_name': 'researcher'
        }, format='json')
        self.assertEqual(artifact_response.status_code, 200)
        self.assertEqual(Artifact.objects.filter(ticket=ticket).count(), 1)

        # 4. Paperclip fires status webhook (needs approval)
        status_response = api.post('/api/webhooks/paperclip/status/', {
            'issue_id': 'pc-e2e-999',
            'new_status': 'needs_approval'
        }, format='json')
        self.assertEqual(status_response.status_code, 200)

        # 5. Verify Django state is correct
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'needs_approval')

        # 6. Verify Telegram task was triggered
        mock_notify_delay.assert_called_once()

    def test_ticket_not_found_returns_404(self):
        api = APIClient()
        response = api.post('/api/webhooks/paperclip/status/', {
            'issue_id': 'nonexistent-id',
            'new_status': 'needs_approval'
        }, format='json')
        self.assertEqual(response.status_code, 404)
