from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Ticket, Artifact


class PaperclipStatusWebhookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ticket = Ticket.objects.create(
            title="Fix login bug",
            description="OAuth flow broken",
            status="new",
            paperclip_issue_id="pp-123",
        )

    def test_webhook_returns_200(self):
        payload = {"event": "issue.updated", "issue_id": "pp-123", "new_status": "in_progress"}
        response = self.client.post(
            "/api/webhooks/paperclip/status/", payload, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_webhook_updates_ticket_status(self):
        payload = {"event": "issue.updated", "issue_id": "pp-123", "new_status": "in_progress"}
        self.client.post("/api/webhooks/paperclip/status/", payload, format="json")
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "in_progress")

    def test_webhook_unknown_issue_returns_404(self):
        payload = {"event": "issue.updated", "issue_id": "pp-DOESNOTEXIST", "status": "done"}
        response = self.client.post(
            "/api/webhooks/paperclip/status/", payload, format="json"
        )
        self.assertEqual(response.status_code, 404)


class PaperclipArtifactWebhookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ticket = Ticket.objects.create(
            title="Fix login bug",
            description="OAuth flow broken",
            status="new",
            paperclip_issue_id="pp-123",
        )

    def test_artifact_webhook_returns_200(self):
        payload = {
            "issue_id": "pp-123",
            "artifact_type": "document",
            "content": "some content",
        }
        response = self.client.post(
            "/api/webhooks/paperclip/artifact/", payload, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_artifact_webhook_creates_artifact(self):
        payload = {
            "issue_id": "pp-123",
            "artifact_type": "document",
            "content": "some content",
        }
        self.client.post("/api/webhooks/paperclip/artifact/", payload, format="json")
        self.assertEqual(Artifact.objects.count(), 1)

    def test_artifact_linked_to_ticket(self):
        payload = {
            "issue_id": "pp-123",
            "artifact_type": "document",
            "content": "some content",
        }
        self.client.post("/api/webhooks/paperclip/artifact/", payload, format="json")
        artifact = Artifact.objects.first()
        self.assertEqual(artifact.ticket, self.ticket)
