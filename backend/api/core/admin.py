"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
  """Define the admin pages for users."""

  ordering = ['id']
  list_display = ['id','email', 'name']

  fieldsets = (
    (None, {'fields' : ('email','password')}),
    (
      _('Permissions'),
      {
        'fields' : (
          'is_active',
          'is_staff',
          'is_superuser',
        ),
      }
    ),
    (_('Important dates'), {'fields' : ('last_login',)}),
  )

  readonly_fields = ('last_login',)

  add_fieldsets = (
    (None, {
      'classes' : ('wide',),
      'fields' : (
        'email',
        'password1',
        'password2',
        'name',
        'is_active',
        'is_staff',
        'is_superuser',
      )
    }),
  )

admin.site.register(models.User, UserAdmin)

class SmartphoneAdmin(admin.ModelAdmin):
  """Define the admin pages for smartphones."""

  ordering = ['-id']
  search_fields = ('name', 'tags',  'user', )
  list_display = ['name', 'price', 'user']

  fieldsets = (
    (None, {'fields' : ('name', 'price', 'description', 'video', 'images', 'tags', )}),
  )
  def save_model(self, request, obj, form, change):
    if getattr(obj, 'user', None) is None:
        obj.user = request.user
    obj.save()

admin.site.register(models.Smartphone, SmartphoneAdmin)

class TagAdmin(admin.ModelAdmin):
  """ Define the admin pages for tags."""
  ordering = ['id']
  search_fields = ('name', )
  list_display = ['name', 'user']

  fieldsets = (
    (None, {'fields' : ('name', )}),
  )
  def save_model(self, request, obj, form, change):
    if getattr(obj, 'user', None) is None:
        obj.user = request.user
    obj.save()

admin.site.register(models.Tag, TagAdmin)

class SmartphoneImageAdmin(admin.ModelAdmin):
  """ Define the admin pages for smartphone images."""
  ordering = ['-id']
  search_fields = ('user', )
  list_display = ['id', 'user']

  fieldsets = (
    (None, {'fields' : ( 'image', )}),
  )
  def save_model(self, request, obj, form, change):
    if getattr(obj, 'user', None) is None:
        obj.user = request.user
    obj.save()

admin.site.register(models.SmartphoneImage, SmartphoneImageAdmin)