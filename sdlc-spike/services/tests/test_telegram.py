from unittest.mock import patch
from django.test import TestCase
from services.telegram_notifier import send_notification

class TelegramNotifierTest(TestCase):
    @patch("services.telegram_notifier.requests.post")
    def test_send_notification_calls_telegram_api(self, mock_post):
        mock_post.return_value.status_code = 200
        send_notification("Ticket #123 needs approval")
        self.assertTrue(mock_post.called)
    @patch("services.telegram_notifier.requests.post")
    def test_send_notification_includes_message(self, mock_post):
        mock_post.return_value.status_code = 200
        send_notification("Ticket #123 needs approval")
        call_body = mock_post.call_args[1]['json']
        self.assertEqual(call_body['text'], "Ticket #123 needs approval")
        
        
