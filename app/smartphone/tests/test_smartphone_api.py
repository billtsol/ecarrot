"""
Tests for smartphone APIs
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status # type: ignore
from rest_framework.test import APIClient # type: ignore

from core.models import (
  Smartphone,
  Tag
)

from smartphone.serializers import (
  SmartphoneSerializer,
  SmartphoneDetailSerializer
)

SMARTPHONE_URLS = reverse('smartphone:smartphone-list')

def detail_url(smartphone_id):
  """Create and return smartphone detail URL."""
  return reverse('smartphone:smartphone-detail', args=[smartphone_id])

def create_smartphone(user, **params):
  """Create and return a sample smartphone"""
  defaults = {
    'name': 'Sample Smartphone',
    'price': Decimal('100.00'),
  }
  defaults.update(params)

  return Smartphone.objects.create(user=user, **defaults)

def create_user(**params):
  """Create and return a sample user"""
  return get_user_model().objects.create_user(**params)

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
    self.user = create_user(
      email = 'userTeset12@example.com',
      password = 'test123456'
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
    other_user = create_user(
      email = 'testUser2@example.com',
      password = 'test123456'
    )
    create_smartphone(user=other_user)

    create_smartphone(user=self.user)

    res = self.client.get(SMARTPHONE_URLS)

    smartphone = Smartphone.objects.filter(user=self.user)
    serializer = SmartphoneSerializer(smartphone, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)


  def test_get_smartphone_detail(self):
    """Test get smartphone detail"""

    smartphone = create_smartphone(user=self.user)

    url = detail_url(smartphone.id)
    res = self.client.get(url)

    serializer = SmartphoneDetailSerializer(smartphone)

    self.assertEqual(res.data, serializer.data)

  def test_create_smartphone(self):
    """Test creating a new smartphone"""
    payload = {
      'name': 'Test Smartphone',
      'price': Decimal('100.00'),
    }

    res = self.client.post(SMARTPHONE_URLS, payload)

    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    smartphone = Smartphone.objects.get(id=res.data['id'])

    for key, value in payload.items():
      self.assertEqual(getattr(smartphone, key), value)

    self.assertEqual(smartphone.user, self.user)

  def test_partial_update(self):
    """Test partial update of a smartphone"""
    original_price = Decimal('100.00')

    smartphone = create_smartphone(
      user = self.user,
      name = "Iphone 1 test",
      price = original_price
    )

    payload = {
      'name': 'Iphone 1'
    }

    url = detail_url(smartphone.id)
    res = self.client.patch(url, payload)

    self.assertEqual(res.status_code, status.HTTP_200_OK)

    smartphone.refresh_from_db()

    self.assertEqual(smartphone.name, payload['name'])
    self.assertEqual(smartphone.price, original_price)
    self.assertEqual(smartphone.user, self.user)

  def test_full_update(self):
    """Test full update of a smartphone"""

    smartphone = create_smartphone(
      user = self.user,
      name = "Iphone 1 test",
      price = Decimal('100.00')
    )

    payload = {
      'name': 'Iphone 2',
      'price': Decimal('200.00')
    }

    url = detail_url(smartphone.id)
    res = self.client.put(url, payload)

    self.assertEqual(res.status_code, status.HTTP_200_OK)

    smartphone.refresh_from_db()

    for key, value in payload.items():
      self.assertEqual(getattr(smartphone, key), value)

    self.assertEqual(smartphone.user, self.user)

  def test_update_user_returns_error(self):
    """Test that update user returns error"""

    new_user = create_user(
      email = 'user1@example.com',
      password = 'test123456'
    )

    smartphone = create_smartphone(user=self.user)

    payload = {'user': new_user.id}
    url = detail_url(smartphone.id)
    self.client.patch(url, payload)

    smartphone.refresh_from_db()
    self.assertEqual(smartphone.user, self.user)

  def test_delete_smartphone(self):
    """Test delete a smartphone"""

    smartphone = create_smartphone(user=self.user)

    url = detail_url(smartphone.id)
    res = self.client.delete(url)

    self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    self.assertFalse(Smartphone.objects.filter(id=smartphone.id).exists())

  def test_delete_smartphone_other_users_smartphone_error(self):
    """Test that authenticated user cannot delete other user's smartphone"""

    new_user = create_user(
      email = 'user98@example.com',
      password = 'test123456'
    )

    smartphone = create_smartphone(user=new_user)

    url = detail_url(smartphone.id)
    res = self.client.delete(url)

    self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
    self.assertTrue(Smartphone.objects.filter(id=smartphone.id).exists())

  def test_create_smartphone_with_new_tags(self):
    """Test creating a new smartphone with new tags"""

    payload = {
      'name': 'Test Smartphone2',
      'price': Decimal('100.00'),
      'tags': [
        {'name' : 'tag12'},
        { 'name' : 'tag22'}
      ]
    }

    res = self.client.post(SMARTPHONE_URLS, payload, format='json')

    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    smartphones = Smartphone.objects.filter(user = self.user)
    self.assertEqual(smartphones.count(), 1)

    smartphone = smartphones[0]
    self.assertEqual(smartphone.tags.count(), 2)

    for tag in payload['tags']:
      exists = smartphone.tags.filter(
        name = tag['name'],
        user = self.user
      ).exists()
      self.assertTrue(exists)

  def test_create_smartphone_with_existing_tags(self):
    """Test creating a new smartphone with existing tags"""

    tag1 = Tag.objects.create(user=self.user, name='tag1')
    tag2 = Tag.objects.create(user=self.user, name='tag2')

    payload = {
      'name': 'Test Smartphone',
      'price': Decimal('100.00'),
      'tags': [
        {'name' : 'tag1'},
        {'name' : 'tag3'}
      ]
    }

    res = self.client.post(SMARTPHONE_URLS, payload, format='json')

    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    smartphones = Smartphone.objects.filter(user = self.user)
    self.assertEqual(smartphones.count(), 1)

    smartphone = smartphones[0]
    self.assertEqual(smartphone.tags.count(), 2)

    self.assertIn(tag1, smartphone.tags.all())

    for tag in payload['tags']:
      exists = smartphone.tags.filter(
        name = tag['name'],
        user = self.user
      ).exists()
      self.assertTrue(exists)

  def test_create_tag_on_update(self):
    """Test create tag when updating a smartphone"""
    smartphone = create_smartphone(user=self.user)

    payload = {
      'tags': [
        {'name': 'tag0'}
      ]
    }
    url = detail_url(smartphone.id)
    res = self.client.patch(url, payload, format='json')

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    new_tag = Tag.objects.get(name = 'tag0', user = self.user)
    self.assertIn(new_tag, smartphone.tags.all())

  def test_update_smartphone_assign_tag(self):
    """Test assigning an existing tag when updating a smartphone"""
    tag_iphone = Tag.objects.create(user=self.user, name='tag_iphone')
    smartphone = create_smartphone(user=self.user)
    smartphone.tags.add(tag_iphone)

    tag_android = Tag.objects.create(user=self.user, name='tag_android')
    payload = { 'tags' : [{'name': 'tag_android'}] }
    url = detail_url(smartphone.id)
    res = self.client.patch(url, payload, format='json')

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertIn(tag_android, smartphone.tags.all())
    self.assertNotIn(tag_iphone, smartphone.tags.all())

  def test_clear_smartphone_tags(self):
    """Test clearing tags when updating a smartphone"""
    tag_iphone = Tag.objects.create(user=self.user, name='tag_iphone2')
    smartphone = create_smartphone(user=self.user)
    smartphone.tags.add(tag_iphone)

    payload = { 'tags' : [] }
    url = detail_url(smartphone.id)
    res = self.client.patch(url, payload, format='json')

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(smartphone.tags.count(), 0)