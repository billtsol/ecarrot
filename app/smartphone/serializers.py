"""
Serializers for smartphone APIs
"""

from rest_framework import serializers # type: ignore
from core.models import (
    Smartphone,
    Tag
)

class SmartphoneSerializer(serializers.ModelSerializer):
    """Serializer for smartphone objects"""

    class Meta:
        model = Smartphone
        fields = ('id', 'name', 'price',)
        read_only_fields = ('id',)

class SmartphoneDetailSerializer(SmartphoneSerializer):
    """Serializer for smartphone detail view."""

    class Meta(SmartphoneSerializer.Meta):
        feilds = SmartphoneSerializer.Meta.fields + ('description',)

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)