from house.serializers.house import HouseSerializer

__all__ = (
    'HouseCreateSerializer',
)


class HouseCreateSerializer(HouseSerializer):
    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        # amenities = validated_data.pop('amenities')
        # facilities = validated_data.pop('facilities')
        #
        # house = House.objects.create(**validated_data)
        #
        # for amenity in amenities:
        #     house.amenities.add(amenity)
        #
        # for facility in facilities:
        #     house.facilities.add(facility)
        #
        # return house
        return super().create(validated_data)
