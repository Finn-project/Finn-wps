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
    disable_days = serializers.SlugRelatedField(many=True, read_only=True, slug_field='date')
    img_cover = serializers.ImageField()
    img_cover_thumbnail = serializers.ImageField(read_only=True)
    house_images = serializers.SerializerMethodField()


    class Meta:
        model = House
        fields = (
            'pk',
            'house_type',
            'name',
            'description',
            'room',
            'bed',
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
            # 'address2',
            'latitude',
            'longitude',
            'disable_days',
            'img_cover',
            'img_cover_thumbnail',
            'house_images',
        )
        read_only_fields = (
            'pk',
            'host',
            'created_date',
            'modified_date',
            'disable_days',
            'img_cover_thumbnail',
        )

    def get_house_images(self, obj):
        name_list = list()
        for house_image in obj.images.all():
            name_list.append(self.context.get('request').build_absolute_uri(house_image.image.url))
        return name_list
