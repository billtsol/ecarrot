"""
Tests for the Smartphone Image API
"""
import tempfile
import os

from PIL import Image # type: ignore

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status # type: ignore
from rest_framework.test import APIClient # type: ignore

from core.models import SmartphoneImage

from smartphone.serializers import SmartphoneImageSerializer

SMARTPHONE_IMAGES_URL = reverse('smartphone:smartphoneimage-list')

def create_user(email = 'test4@example.com', password = 'test123456'):
  """Create a user"""
  return get_user_model().objects.create_user(
    email = email,
    password = password
  )

def detail_url(image_id):
  """Return the URL for the tag detail"""
  return reverse('smartphone:smartphoneimage-detail', args=[image_id])

def create_smartphone_image(name = 'test_image.jpg'):
  """Create a smartphone image"""
  image = SimpleUploadedFile(
    name,
    b"file_content",
    content_type="image/jpeg"
  )
  return image

class PublicSmartphoneImagesApiTests(TestCase):
  """Test unauthenticated API requests"""

  def setUp(self):
    self.client = APIClient()

  def test_auth_required(self):
    """Test auth is required for retrieving images"""

    res = self.client.get(SMARTPHONE_IMAGES_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateSmartphoneImagesApiTests(TestCase):
  """Test authenticated API requests"""

  def setUp(self):
    self.user = create_user()
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def test_retrieve_smartphone_images(self):
    """Test retrieving a list of images"""

    SmartphoneImage.objects.create(
      user = self.user,
      image = create_smartphone_image('test1.jpg')
    )
    SmartphoneImage.objects.create(
      user = self.user,
      image = create_smartphone_image('test2.jpg')
    )

    res = self.client.get(SMARTPHONE_IMAGES_URL)

    images = SmartphoneImage.objects.all().order_by('-id')
    serializer = SmartphoneImageSerializer(images, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(len(res.data), len(serializer.data))

  def test_update_smartphone_image(self):
    """Test updating a smartphone image"""

    smartphone_image = SmartphoneImage.objects.create(
      user = self.user,
      image = create_smartphone_image('test3.jpg')
    )

    with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
      img = Image.new('RGB', (10, 10))
      img.save(image_file, format='JPEG')
      image_file.seek(0)
      payload = {'image': image_file}

      url = detail_url(smartphone_image.id)
      res = self.client.patch(url, payload, format='multipart')

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertTrue(os.path.exists(smartphone_image.image.path))

  def test_delete_smartphone_image(self):
    """Test deleting a smartphone image"""
    smartphone_image = SmartphoneImage.objects.create(
      user = self.user,
      image = create_smartphone_image('test4.jpg')
    )

    url = detail_url(smartphone_image.id)
    res = self.client.delete(url)

    self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    smartphone_images = SmartphoneImage.objects.filter(user = self.user)
    self.assertFalse(smartphone_images.exists())