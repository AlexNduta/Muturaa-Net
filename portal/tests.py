from django.test import TestCase, Client
from django.urls import reverse

class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_connect_view(self):
        response = self.client.get(reverse('connect_view'), {'id': '00:11:22:33:44:55'})
        self.assertEqual(response.status_code, 200)

    def test_wait_for_payment_view(self):
        from .models import GuestSession
        session = GuestSession.objects.create(mac_address='00:11:22:33:44:55')
        response = self.client.get(reverse('wait_for_payment_view', args=[session.id]))
        self.assertEqual(response.status_code, 200)
