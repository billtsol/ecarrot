"""
Views for smartphone APIs
"""

from rest_framework import ( # type: ignore
  viewsets,
  mixins
)
from rest_framework.authentication import TokenAuthentication # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore

from core.models import (
  Smartphone,
  Tag
)
from smartphone import serializers

class SmartphoneViewSet(viewsets.ModelViewSet):
  """Manage smartphones in the database"""

  serializer_class = serializers.SmartphoneDetailSerializer
  queryset = Smartphone.objects.all()
  authentication_classes = (TokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def get_queryset(self):
    """Retrieve Smartphone for authenticated users"""
    return self.queryset.filter(user = self.request.user).order_by('-id')

  def get_serializer_class(self):
    """Return the serializer class for request"""

    if self.action == 'list':
      return serializers.SmartphoneSerializer

    return self.serializer_class

  def perform_create(self, serializer):
    """Create a new smartphone"""
    serializer.save(user=self.request.user)

class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
  """Manage tags in the database"""

  serializer_class = serializers.TagSerializer
  queryset = Tag.objects.all()
  authentication_classes = (TokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def get_queryset(self):
    """Retrieve tags for the authenticated user"""
    return self.queryset.filter(user = self.request.user).order_by('-name')