from house.serializers.house import HouseSerializer

__all__ = (
    'HouseCreateSerializer',
)


class HouseCreateSerializer(HouseSerializer):
    def validate(self, attrs):
        return attrs
