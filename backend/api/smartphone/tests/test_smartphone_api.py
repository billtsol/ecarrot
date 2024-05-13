"""
Tests for smartphone APIs
"""

from decimal import Decimal
import tempfile
import os

from PIL import Image # type: ignore

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status # type: ignore
from rest_framework.test import APIClient # type: ignore

from core.models import (
  Smartphone,
  Tag,
  SmartphoneImage
)

from smartphone.serializers import (
  SmartphoneSerializer
)

SMARTPHONE_URLS = reverse('smartphone:smartphone-list')
SMARTPHONE_IMAGES_URL = reverse('smartphone:smartphoneimage-list')

def detail_url(smartphone_id):
  """Create and return smartphone detail URL."""
  return reverse('smartphone:smartphone-detail', args=[smartphone_id])

def image_upload_url(smartphone_id):
  """Return URL for smartphone image upload"""
  return reverse('smartphone:smartphone-upload-image', args=[smartphone_id])

def create_smartphone(user, **params):
  """Create and return a sample smartphone"""
  defaults = {
    'name': 'Sample Smartphone',
    'price': Decimal('100.00'),
  }
  defaults.update(params)

  return Smartphone.objects.create(user=user, **defaults)

def create_smartphone_image(name = 'test_image.jpg'):
  """Create a smartphone image"""
  image = SimpleUploadedFile(
    name,
    b"file_content",
    content_type="image/jpeg"
  )
  return image

def create_user(**params):
  """Create and return a sample user"""
  return get_user_model().objects.create_user(**params)

class PublicSmartphoneApiTests(TestCase):
  """Test the publicly available smartphone API for unauthenticated users"""

  def setUp(self):
    self.client = APIClient()

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

  # def test_smartphone_list_limited_to_user(self):
  #   """Test that smartphones for the authenticated user are returned"""
  #   other_user = create_user(
  #     email = 'testUser2@example.com',
  #     password = 'test123456'
  #   )
  #   create_smartphone(user=other_user)

  #   create_smartphone(user=self.user)

  #   res = self.client.get(SMARTPHONE_URLS)

  #   smartphone = Smartphone.objects.filter(user=self.user)
  #   serializer = SmartphoneSerializer(smartphone, many=True)

  #   self.assertEqual(res.status_code, status.HTTP_200_OK)
  #   self.assertEqual(res.data, serializer.data)

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
        {'name' : 'tag2'}
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

  def test_create_smartphone_with_new_images(self):
    """Test creating a new smartphone with new images"""

    test_image1 = create_smartphone_image('test_image1.jpg')
    test_image2 = create_smartphone_image('test_image2.jpg')

    image1 = SmartphoneImage.objects.create(
      user = self.user,
      image = test_image1
    )
    image2 = SmartphoneImage.objects.create(
      user = self.user,
      image = test_image2
    )

    payload = {
      'name': 'Test Smartphone3',
      'price': Decimal('100.00'),
      'images': [
        image1,
        image2
      ]
    }

    res = self.client.post(SMARTPHONE_URLS, payload, format='multipart')

    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_filter_by_tags(self):
    """Test filtering smartphones by tags"""

    smartphone1 = create_smartphone( user = self.user, name = 'Iphone 1')
    smartphone2 = create_smartphone( user = self.user, name = 'Iphone 2')

    tag1 = Tag.objects.create(user=self.user, name='tag1')
    tag2 = Tag.objects.create(user=self.user, name='tag2')

    smartphone1.tags.add(tag1)
    smartphone2.tags.add(tag2)

    smartphone3 = create_smartphone(user=self.user, name='Iphone 3')

    params = { 'tags': f'{tag1.id},{tag2.id}' }
    res = self.client.get(SMARTPHONE_URLS, params)

    s1 = SmartphoneSerializer(smartphone1)
    s2 = SmartphoneSerializer(smartphone2)
    s3 = SmartphoneSerializer(smartphone3)

    self.assertIn(s1.data, res.data)
    self.assertIn(s2.data, res.data)
    self.assertNotIn(s3.data, res.data)

  def test_create_smartphone_with_new_video(self):
    """Test creating a new smartphone with new video"""

    with tempfile.NamedTemporaryFile(suffix='.mp4') as video_file:
      video_file.write(b"file_content")
      video_file.seek(0)

      payload = {
        'name': 'Test Smartphone3',
        'price': Decimal('100.00'),
        'video': video_file
      }

      res = self.client.post(SMARTPHONE_URLS, payload, format='multipart')

      self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_update_smartphone_video(self):
    """Test updating a smartphone with new video"""

    with tempfile.NamedTemporaryFile(suffix='.mp4') as video_file:
      video_file.write(b"file_content")
      video_file.seek(0)

      smartphone = create_smartphone(user=self.user)

      payload = { 'video': video_file }
      url = detail_url(smartphone.id)
      res = self.client.patch(url, payload, format='multipart')

      self.assertEqual(res.status_code, status.HTTP_200_OK)