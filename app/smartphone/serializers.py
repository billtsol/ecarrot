"""
Serializers for smartphone APIs
"""

from rest_framework import serializers # type: ignore
from core.models import (
    Smartphone,
    Tag
)

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)

class SmartphoneSerializer(serializers.ModelSerializer):
    """Serializer for smartphone objects"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Smartphone
        fields = ('id', 'name', 'price','tags',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        """Create and return a new smartphone"""
        tags = validated_data.pop('tags', [])

        smartphone = Smartphone.objects.create(**validated_data)
        auth_user = self.context['request'].user

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user = auth_user,
                **tag,
            )
            smartphone.tags.add(tag_obj)

        return smartphone

class SmartphoneDetailSerializer(SmartphoneSerializer):
    """Serializer for smartphone detail view."""

    class Meta(SmartphoneSerializer.Meta):
        feilds = SmartphoneSerializer.Meta.fields + ('description',)
