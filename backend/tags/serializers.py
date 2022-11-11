from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagListField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'color': obj.color,
            'slug': obj.slug
        }

    def to_internal_value(self, data):
        try:
            return Tag.objects.get(id=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Недопустимый первичный ключ "404" - объект не существует.'
            )
