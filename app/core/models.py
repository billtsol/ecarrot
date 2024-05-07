"""
Database for models
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
  AbstractBaseUser,
  BaseUserManager,
  PermissionsMixin,
)

def smartphone_image_file_path(instance, filename):
  """Generate file path for new smartphone image."""
  ext = os.path.splitext(filename)[1]
  filename = f'{uuid.uuid4()}{ext}'

  return os.path.join('uploads', 'smartphone', filename)

class UserManager(BaseUserManager):
  """Manager for user in the system"""

  def create_user(self, email, password=None, **extra_fields):
    """Create save and return a new user"""
    if not email:
      raise ValueError('Users must have an email address')

    user = self.model(
      email=self.normalize_email(email),
      **extra_fields
    )
    user.set_password(password)
    user.save(using=self._db)

    return user

  def create_superuser(self, email, password):
    """Create and save a new superuser"""
    user = self.create_user(email, password)
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)

    return user

class User(AbstractBaseUser, PermissionsMixin):
  """User in the system"""
  email = models.EmailField(max_length=255, unique=True)
  name = models.CharField(max_length=255)

  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)

  objects = UserManager()

  USERNAME_FIELD = 'email' # Default username field for authentication

class Smartphone(models.Model):
  """Smartphone object."""

  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
  )

  name = models.CharField(max_length=255)
  price = models.DecimalField(max_digits=5, decimal_places=2)
  description = models.TextField(blank=True)
  tags = models.ManyToManyField('Tag')

  images = models.ManyToManyField('SmartphoneImage')

  def __str__(self):
    return self.name

class Tag(models.Model):
  """Tag for filtering object."""
  name = models.CharField(max_length=255)
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
  )

  def __str__(self):
    return self.name

class SmartphoneImage(models.Model):
  """Smartphone image object."""
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
  )

  image = models.ImageField(upload_to = smartphone_image_file_path)

  def __str__(self):
    return str(self.id)