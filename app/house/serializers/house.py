# from rest_framework import serializers
#
# from members.serializers import UserSerializer
# from ..models import (
#     House,
#     Amenities,
#     Facilities,
#     HouseImage
# )
#
#
# class AmenitiesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Amenities
#         fields = (
#             'pk',
#             'name',
#         )
#
#
# class FacilitiesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Facilities
#         fields = (
#             'pk',
#             'name',
#         )
#
#
# class HouseImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HouseImage
#         fields = '__all__'
#
#
# class HouseSerializer(serializers.ModelSerializer):
#     amenities = AmenitiesSerializer(many=True, read_only=True)
#     facilities = FacilitiesSerializer(many=True, read_only=True)
#
#     # house_images = HouseImageSerializer(many=True, read_only=True)
#     host = UserSerializer(read_only=True)
#
#     class Meta:
#         model = House
#         fields = (
#             'pk',
#             'house_type',
#             'name',
#             'description',
#             'room',
#             'bathroom',
#             'personnel',
#             'amenities',
#             'facilities',
#             'minimum_check_in_duration',
#             'maximum_check_in_duration',
#             # 'start_day_for_break',
#             # 'end_day_for_break',
#             'maximum_check_in_range',
#             'price_per_night',
#             'created_date',
#             'modified_date',
#             'host',
#             'country',
#             'city',
#             'district',
#             'dong',
#             'address1',
#             'address2',
#             'latitude',
#             'longitude'
#         )

from rest_framework import serializers

from members.serializers import UserSerializer
from ..models import (
    House,
)

__all__ = (
    'HouseSerializer',
)


class HouseSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)

    class Meta:
        model = House
        fields = (
            'pk',
            'house_type',
            'name',
            'description',
            'room',
            'bathroom',
            'personnel',
            'amenities',
            'facilities',
            'minimum_check_in_duration',
            'maximum_check_in_duration',
            'maximum_check_in_range',
            'price_per_night',
            'created_date',
            'modified_date',
            'host',
            'country',
            'city',
            'district',
            'dong',
            'address1',
            'address2',
            'latitude',
            'longitude'
        )
        read_only_fields = (
            'pk',
            'host',
            'created_date',
            'modified_date',
        )
