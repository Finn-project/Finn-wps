from rest_framework.fields import ImageField

from house.serializers.house import HouseSerializer

__all__ = (
    'HouseCreateSerializer',
)


class HouseCreateSerializer(HouseSerializer):
    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        if validated_data.get('img_cover'):
            validated_data.pop('img_cover')
        return super().create(validated_data)
