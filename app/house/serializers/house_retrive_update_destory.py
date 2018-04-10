from ..serializers import HouseSerializer

__all__ = (
    'HouseRetrieveUpdateDestroySerializer',
)


class HouseRetrieveUpdateDestroySerializer(HouseSerializer):
    def validate(self, attrs):
        pass

    def update(self, instance, validated_data):
        return instance
