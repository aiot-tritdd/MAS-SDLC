from rest_framework.test import APIClient
from django.test import TestCase
from core.models import Ticket

class TicketAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
    def test_create_ticket_returns_201(self):
        payload = {
            "title": "Add auth endpoint",
            "description": "Implement JWT authentication for the API",
        }
        response = self.client.post('/api/tickets/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Ticket.objects.filter(title="Add auth endpoint").exists())
    def test_create_ticket_saves_to_db(self):
        payload = {
            'title': 'Add auth endpoint',
            'description': 'Implement JWT authentication for the API',
        }
        self.client.post('/api/tickets/', payload, format='json')
        self.assertEqual(Ticket.objects.count(), 1)
    def test_create_ticket_default_status_is_new(self):
        payload = {'title': 'Test', 'description': 'desc'}
        response = self.client.post('/api/tickets/', payload, format='json')
        self.assertEqual(response.data['status'], 'new')
    def test_list_tickets_returns_all(self):
        Ticket.objects.create(title="T1", description="d1")
        Ticket.objects.create(title="T2", description='d2')
        response = self.client.get('/api/tickets/')
        self.assertEqual(len(response.data), 2)
