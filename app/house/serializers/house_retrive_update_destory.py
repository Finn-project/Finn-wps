from ..serializers import HouseSerializer

__all__ = (
    'HouseRetrieveUpdateDestroySerializer',
)


class HouseRetrieveUpdateDestroySerializer(HouseSerializer):
    def validate(self, attrs):
        return attrs

    def update(self, instance, validated_data):
        if validated_data.get('img_cover'):
            validated_data.pop('img_cover')
        return super().update(instance, validated_data)
