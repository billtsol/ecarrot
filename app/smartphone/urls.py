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
router.register('smartphones', views.SmartphoneViewSet)

app_name = 'smartphones'

urlpatterns = [
    path('', include(router.urls))
]
