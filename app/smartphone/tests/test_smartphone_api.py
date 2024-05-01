"""
Tests for smartphone APIs
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status # type: ignore
from rest_framework.test import APIClient # type: ignore

from core.models import Smartphone
from smartphone.serializers import SmartphoneSerializer

SMARTPHONE_URLS = reverse('smartphone:smartphone-list')

def create_smartphone(user, **params):
  """Create and return a sample smartphone"""
  defaults = {
    'name': 'Sample Smartphone',
    'price': Decimal('100.00'),
  }
  defaults.update(params)

  return Smartphone.objects.create(user=user, **defaults)


class PublicSmartphoneApiTests(TestCase):
  """Test the publicly available smartphone API for unauthenticated users"""

  def setUp(self):
    self.client = APIClient()

  def test_auth_required(self):
    """Test that auth is required for retrieving smartphones"""
    res = self.client.get(SMARTPHONE_URLS)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateSmartphoneApiTests(TestCase):
  """Test the authorized user smartphone API"""

  def setUp(self):
    self.client = APIClient()
    self.user = get_user_model().objects.create_user(
      'userTeset12@example.com',
      'test123456'
    )
    self.client.force_authenticate(self.user)

  def test_retrieve_smartphones(self):
    """Test retrieving a list of smartphones"""
    create_smartphone(user=self.user)
    create_smartphone(user=self.user)

    res = self.client.get(SMARTPHONE_URLS)

    smartphones = Smartphone.objects.all().order_by('-id')
    serializer = SmartphoneSerializer(smartphones, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  def test_smartphone_list_limited_to_user(self):
    """Test that smartphones for the authenticated user are returned"""
    other_user = get_user_model().objects.create_user(
      'testUser2@example.com',
      'test123456'
    )
    create_smartphone(user=other_user)

    create_smartphone(user=self.user)

    res = self.client.get(SMARTPHONE_URLS)

    smartphone = Smartphone.objects.filter(user=self.user)
    serializer = SmartphoneSerializer(smartphone, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)