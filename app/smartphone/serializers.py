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

    def _get_or_create_tags(self, tags, instance):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user = auth_user,
                **tag,
            )
            instance.tags.add(tag_obj)

    def create(self, validated_data):
        """Create and return a new smartphone"""
        tags = validated_data.pop('tags', [])
        smartphone = Smartphone.objects.create(**validated_data)

        self._get_or_create_tags(tags, smartphone)

        return smartphone

    def update(self, instance, validated_data):
        """Update and return a smartphone"""
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class SmartphoneDetailSerializer(SmartphoneSerializer):
    """Serializer for smartphone detail view."""

    class Meta(SmartphoneSerializer.Meta):
        feilds = SmartphoneSerializer.Meta.fields + ('description',)
