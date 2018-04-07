from rest_framework import serializers

from ..models import HouseLocation


class HouseLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseLocation
        fields = '__all__'
