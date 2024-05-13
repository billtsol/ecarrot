"""
Url mapping for the smartphone app.
"""

from django.urls import (
  path,
  include
)

from rest_framework.routers import DefaultRouter # type: ignore
from smartphone import views

router = DefaultRouter()
router.register('smartphone', views.SmartphoneViewSet)
router.register('tags', views.TagViewSet)
router.register('smartphoneimage', views.SmartphoneImageViewSet)

app_name = 'smartphone'

urlpatterns = [
    path('', include(router.urls))
]
