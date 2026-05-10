from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Ticket


class PaperclipWebhookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ticket = Ticket.objects.create(
            title="Fix login bug",
            description="OAuth flow broken",
            paperclip_issue_id="pp-123",
        )

    def test_webhook_returns_200(self):
        payload = {"event": "issue.updated", "issue_id": "pp-123", "status": "in_progress"}
        response = self.client.post("/api/webhooks/paperclip/", payload, format="json")
        self.assertEqual(response.status_code, 200)

    def test_webhook_updates_ticket_status(self):
        payload = {"event": "issue.updated", "issue_id": "pp-123", "status": "in_progress"}
        self.client.post("/api/webhooks/paperclip/", payload, format="json")
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "in_progress")

    def test_webhook_unknown_issue_returns_404(self):
        payload = {"event": "issue.updated", "issue_id": "pp-DOESNOTEXIST", "status": "done"}
        response = self.client.post("/api/webhooks/paperclip/", payload, format="json")
        self.assertEqual(response.status_code, 404)
