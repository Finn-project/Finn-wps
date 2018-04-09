from rest_framework import serializers

from ..models import (
    House,
)


class HouseCreateSerializer(serializers.ModelSerializer):
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
            'longitude',
        )

    # def validate_host(self, host):
    #     print('validate_host', host)
    #     return host
    #
    # def validate(self, attrs):
    #     print('\nvalidate : ', attrs)
    #     return attrs
    #
    # def create(self, validated_data):
    #     print('\ncreate : ', validated_data)
    #     print(validated_data['amenities'][0].pk)
    #
    #     return House.objects.create(**validated_data)
    #     # return super().create(validated_data)
