"""
Tests for models
"""

from unittest.mock import patch
from decimal import Decimal
from core import models

from django.test import TestCase
from django.contrib.auth import get_user_model

def create_user(email = 'test2@example.com', password = 'test123456'):
  """Create a user"""
  return get_user_model().objects.create_user(
    email = email,
    password = password
  )

class ModelTests(TestCase):

  def test_create_user_with_email_successful(self):
    """Test creating a new user with an email is successful"""
    email = 'test@example.com'
    password = 'test123456'
    user = get_user_model().objects.create_user(
      email = email,
      password = password
    )

    self.assertEqual(user.email, email)
    self.assertTrue(user.check_password(password))

  def test_new_user_email_normalized(self):
    """Test the email for a new user is normalized"""
    sample_emails = [
      ['test@EXAMPLE.com', 'test@example.com'],
      ['Test2@exampLE.com', 'Test2@example.com'],
      ['test3@exAMple.com', 'test3@example.com'],
    ]

    for email, expected_email in sample_emails:
      user = get_user_model().objects.create_user(
        email = email,
        password = 'password123'
      )

      self.assertEqual(user.email, expected_email)

  def test_new_user_invalid_email(self):
    """Test creating user with no email raises error"""
    with self.assertRaises(ValueError):
      get_user_model().objects.create_user('', 'password123')

  def test_create_superuser(self):
    """Test creating a new superuser"""
    user = get_user_model().objects.create_superuser(
      'testSuper@example.com',
      'testuser12345'
    )

    self.assertTrue(user.is_superuser)
    self.assertTrue(user.is_staff)

  def test_create_smartphone(self):
    """Test creating a smartphone is successful"""
    user = get_user_model().objects.create_user(
      'test@example.com',
      'testuser1234'
    )

    smartphone = models.Smartphone.objects.create(
      user = user,
      name = 'Smartphone 1',
      price = Decimal('9.5')
    )

    self.assertEqual(str(smartphone), smartphone.name)

  def test_create_tag(self):
    """Test creating a tag is successful"""
    user = create_user()
    tag = models.Tag.objects.create(
      user = user,
      name = 'Tag 1'
    )

    self.assertEqual(str(tag), tag.name)

  @patch('core.models.uuid.uuid4')
  def test_smartphone_file_name_uuid(self, mock_uuid):
    """Test generating image path."""
    uuid = 'test-uuid'
    mock_uuid.return_value = uuid
    file_path = models.smartphone_image_file_path(None, 'example.jpg')

    exp_path = f'uploads/smartphone/{uuid}.jpg'
    self.assertEqual(file_path, exp_path)