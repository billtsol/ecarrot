"""
Serializers for smartphone APIs
"""

from rest_framework import serializers # type: ignore
from core.models import (
    Smartphone,
    Tag,
    SmartphoneImage
)

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)

class SmartphoneImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to smartphones"""

    class Meta:
        model = SmartphoneImage
        fields = ('id', 'user', 'image', )
        read_only_fields = ('id',)
        extra_kwargs = {'image': {'required': True}}

    def _create_image(self, validated_data, smartphone):
        """Create a new SmartphoneImage"""

        image = SmartphoneImage.objects.create(**validated_data)
        smartphone.images.add(image)

        return image

class SmartphoneSerializer(serializers.ModelSerializer):
    """Serializer for smartphone objects"""

    tags = TagSerializer(many=True, required=False)
    images = SmartphoneImageSerializer(many=True, required=False)

    class Meta:
        model = Smartphone
        fields = ('id', 'name', 'price','tags', 'description', 'images', 'video', )
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
        images = validated_data.pop('images',[])

        tags = validated_data.pop('tags', [])
        smartphone = Smartphone.objects.create(**validated_data)

        self._get_or_create_tags(tags, smartphone)

        # Make function
        auth_user = self.context['request'].user
        for image in images:
            new_smartphone_image = SmartphoneImage.objects.create(
                user = auth_user,
                **image
            )
            smartphone.images.add(new_smartphone_image)

        return smartphone

    def update(self, instance, validated_data):
        """Update and return a smartphone"""
        tags = validated_data.pop('tags', None)
        images = validated_data.pop('images', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if images is not None:
            instance.images.clear()
            # Make function
            auth_user = self.context['request'].user
            for image in images:
                new_smartphone_image = SmartphoneImage.objects.create(
                    user = auth_user,
                    image = image
                )
                instance.images.add(new_smartphone_image)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
