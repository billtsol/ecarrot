"""
Views for smartphone APIs
"""

from rest_framework import viewsets # type: ignore
from rest_framework.authentication import TokenAuthentication # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore

from core.models import Smartphone
from smartphone import serializers

class SmartphoneViewSet(viewsets.ModelViewSet):
    """Manage smartphones in the database"""

    serializer_class = serializers.SmartphoneSerializer
    queryset = Smartphone.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
      """Retrieve Smartphone for authenticated users"""
      return self.queryset.filter(user = self.request.user).order_by('-id')
