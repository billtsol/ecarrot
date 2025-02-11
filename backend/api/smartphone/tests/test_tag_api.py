"""
Tests for the tags API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status # type: ignore
from rest_framework.test import APIClient # type: ignore

from core.models import Tag

from smartphone.serializers import TagSerializer

TAGS_URL = reverse('smartphone:tag-list')

def create_user(email = 'test3@example.com', password = 'test123456'):
  """Create a user"""
  return get_user_model().objects.create_user(
    email = email,
    password = password
  )

def detail_url(tag_id):
  """Return the URL for the tag detail"""
  return reverse('smartphone:tag-detail', args=[tag_id])


class PublicTagsApiTests(TestCase):
  """Test unauthenticated API requests"""

  def setUp(self):
    self.client = APIClient()

class PrivateTagsApiTests(TestCase):
  """Test authenticated API requests"""

  def setUp(self):
    self.user = create_user()
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def test_retrieve_tags(self):
    """Test retrieving a list of tags"""
    Tag.objects.create(user = self.user, name = 'Test tag')
    Tag.objects.create(user = self.user, name = 'Test tag 2')

    res = self.client.get(TAGS_URL)

    tags = Tag.objects.all().order_by('-name')
    serializer = TagSerializer(tags, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  # def test_tags_limited_to_user(self):
  #   """Test tags returned are for the authenticated user"""
  #   user2 = create_user(
  #     email = 'user2@example.com',
  #     password = 'password123'
  #   )

  #   Tag.objects.create(user = user2, name = 'Test tag 3')

  #   tag = Tag.objects.create(user = self.user, name = 'Test tag 4')

  #   res = self.client.get(TAGS_URL, {'user': self.user.id})

  #   self.assertEqual(res.status_code, status.HTTP_200_OK)
  #   self.assertEqual(len(res.data), 1)
  #   self.assertEqual(res.data[0]['name'], tag.name)
  #   self.assertEqual(res.data[0]['id'], tag.id)

  def test_create_tag(self):
    """Test creating a new tag"""
    payload = {'name': 'Test tag 5'}
    res = self.client.post(TAGS_URL, payload)
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_update_tag(self):
    """Test updating a tag"""
    tag = Tag.objects.create(user = self.user, name = 'Test tag 4')
    payload = {'name': 'New tag name'}

    url = detail_url(tag.id)
    res = self.client.patch(url, payload)

    self.assertEqual(res.status_code, status.HTTP_200_OK)

    tag.refresh_from_db()
    self.assertEqual(tag.name, payload['name'])

  def test_delete_tag(self):
    """Test deleting a tag"""
    tag = Tag.objects.create(user = self.user, name = 'Test tag 5')

    url = detail_url(tag.id)
    res = self.client.delete(url)

    self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    tags = Tag.objects.filter(user = self.user)
    self.assertFalse(tags.exists())