"""
Views for smartphone APIs
"""
import json

from drf_spectacular.utils import ( # type: ignore
  extend_schema_view,
  extend_schema,
  OpenApiParameter,
  OpenApiTypes
)
from rest_framework import ( # type: ignore
  viewsets,
  mixins,
  status
)

from rest_framework.response import Response # type: ignore
from rest_framework.decorators import action # type: ignore
from rest_framework.authentication import TokenAuthentication # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework import generics # type: ignore

from core.models import (
  Smartphone,
  Tag,
  SmartphoneImage
)
from smartphone import serializers

@extend_schema_view(
  list = extend_schema(
    parameters = [
      OpenApiParameter(
        'tags',
        OpenApiTypes.STR,
        description = 'Comma separated list of IDs to filter'
      )
    ]
  )
)
class SmartphoneViewSet(viewsets.ModelViewSet):
  """Manage smartphones in the database"""

  serializer_class = serializers.SmartphoneDetailSerializer
  queryset = Smartphone.objects.all()
  authentication_classes = (TokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def _params_to_ints(self, qs):
    """Convert a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(',')]

  def get_queryset(self):
    """Retrieve Smartphone for authenticated users"""
    tags = self.request.query_params.get('tags')

    queryset = self.queryset

    if tags:
      tag_ids = self._params_to_ints(tags)
      queryset = queryset.filter(tags__id__in = tag_ids)

    return queryset.filter(
      user = self.request.user
    ).order_by('-id').distinct()

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

    payload = {
      'user' : self.request.user,
      'image': request.data['image'],
    }

    if serializer.is_valid():
      image = serializer._create_image(payload, smartphone)
      serializer_data = serializers.SmartphoneImageSerializer(image)
      return Response(serializer_data.data, status=status.HTTP_200_OK)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class TagViewSet(
  mixins.CreateModelMixin,
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

  def perform_create(self, serializer):
    """Create a new smartphone image"""
    serializer.save(user=self.request.user)

class SmartphoneImageViewSet(
  mixins.CreateModelMixin,
  mixins.DestroyModelMixin,
  mixins.UpdateModelMixin,
  mixins.ListModelMixin,
  viewsets.GenericViewSet
):
  """Manage Smartphone images in the database"""

  serializer_class = serializers.SmartphoneImageSerializer
  queryset = SmartphoneImage.objects.all()
  authentication_classes = (TokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def get_queryset(self):
    """Retrieve tags for the authenticated user"""
    return self.queryset.filter(user = self.request.user).order_by('-id')

  def perform_create(self, serializer):
    """Create a new smartphone image"""
    serializer.save(user=self.request.user)