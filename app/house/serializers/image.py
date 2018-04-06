from rest_framework import serializers

from ..models import HouseImage


class HouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseImage
        fields = '__all__'