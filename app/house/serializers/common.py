from rest_framework import serializers

from ..models import (
    House,
    Amenities,
    Facilities,
    HouseLocation,
    HouseImage,
    RelationWithHouseAndGuest
)


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = '__all__'


class AmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenities
        fields = '__all__'


class FacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facilities
        fields = '__all__'


class HouseLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseLocation
        fields = '__all__'


class HouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseImage
        fields = '__all__'


class RelationWithHouseAndGuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationWithHouseAndGuest
        fields = '__all__'
