"""
Views for smartphone APIs
"""

from rest_framework import ( # type: ignore
  viewsets,
  mixins,
  status
)

from rest_framework.response import Response # type: ignore
from rest_framework.decorators import action # type: ignore
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
    elif self.action =='upload_image':
      return serializers.SmartphoneImageSerializer

    return self.serializer_class

  def perform_create(self, serializer):
    """Create a new smartphone"""
    serializer.save(user=self.request.user)

  @action(detail=True, methods=['POST'], url_path = 'upload-image')
  def upload_image(self, request, pk=None):
    """Upload an image to a smartphone"""
    smartphone = self.get_object()
    serializer = self.get_serializer(smartphone, data = request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class TagViewSet(
  mixins.DestroyModelMixin,
  mixins.UpdateModelMixin,
  mixins.ListModelMixin,
  viewsets.GenericViewSet
):
  """Manage tags in the database"""

  serializer_class = serializers.TagSerializer
  queryset = Tag.objects.all()
  authentication_classes = (TokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def get_queryset(self):
    """Retrieve tags for the authenticated user"""
    return self.queryset.filter(user = self.request.user).order_by('-name')