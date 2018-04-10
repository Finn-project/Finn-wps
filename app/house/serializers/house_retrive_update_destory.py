from house.models import House
from ..serializers import HouseSerializer

__all__ = (
    'HouseRetrieveUpdateDestroySerializer',
)


class HouseRetrieveUpdateDestroySerializer(HouseSerializer):
    def validate(self, attrs):
        return attrs
