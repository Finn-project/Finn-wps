from rest_framework import serializers

from house.serializers.common import AmenitiesSerializer, FacilitiesSerializer, HouseLocationSerializer
from members.serializers import UserSerializer


class HouseCreateSerializer(serializers.ModelSerializer):
    house_type = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()

    room = serializers.IntegerField()
    bed = serializers.IntegerField()
    bathroom = serializers.IntegerField()

    personnel = serializers.IntegerField()

    amenities = AmenitiesSerializer(many=True)
    facilities = FacilitiesSerializer(many=True)

    minimum_check_in_duration = serializers.IntegerField()
    maximum_check_in_duration = serializers.IntegerField()

    start_day_for_break = serializers.DateField(format='%Y-%m-%d')
    end_day_for_break = serializers.DateField(format='%Y-%m-%d')

    maximum_check_in_range = serializers.IntegerField()

    DEFAULT_PRICE_PER_NIGHT = 100000
    price_per_night = serializers.IntegerField()

    created_date = serializers.DateField(format='%Y-%m-%d')
    modified_date = serializers.DateField(format='%Y-%m-%d')

    host = UserSerializer(many=True)

    guest = UserSerializer(many=True)

    location = HouseLocationSerializer(many=True)
