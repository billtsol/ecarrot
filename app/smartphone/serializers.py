"""
Serializers for smartphone APIs
"""

from rest_framework import serializers # type: ignore
from core.models import Smartphone

class SmartphoneSerializer(serializers.ModelSerializer):
    """Serializer for smartphone objects"""

    class Meta:
        model = Smartphone
        fields = ('id', 'name', 'price',)
        read_only_fields = ('id',)