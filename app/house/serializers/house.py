from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers

from members.serializers import UserSerializer
from utils.image.resize import clear_imagekit_cache
from ..models import (
    House,
    HouseDisableDay,
)

__all__ = (
    'HouseSerializer',
)


class HouseImageField(serializers.RelatedField):
    def to_representation(self, value):
        if hasattr(value, 'image'):
            if self.context.get('request'):
                return self.context.get('request').build_absolute_uri(value.image.url)
            else:
                return value.image.url


class HouseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    disable_days = serializers.SlugRelatedField(many=True, read_only=True, slug_field='date')
    reserve_days = serializers.SlugRelatedField(many=True, read_only=True, slug_field='date')
    img_cover = serializers.ImageField(required=False)
    img_cover_thumbnail = serializers.ImageField(read_only=True)
    house_images = HouseImageField(many=True, read_only=True, source='images')

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
            'latitude',
            'longitude',
            'disable_days',
            'reserve_days',
            'img_cover',
            'img_cover_thumbnail',
            'house_images',
        )

    def create(self, validated_data):
        validated_data.pop('img_cover', None)

        request = self.context.get('request')

        validated_data['host'] = request.user
        house = super().create(validated_data)

        for date in request.data.getlist('disable_days'):
            date_instance, created = HouseDisableDay.objects.get_or_create(date=date)
            house.disable_days.add(date_instance)

        if request.FILES:
            for img_cover in request.data.getlist('img_cover'):
                house.img_cover.save(img_cover.name, img_cover)

            for room_image in request.data.getlist('house_images'):
                house.images.create_image(image=room_image)

        request.user.is_host = True
        request.user.save()

        return house

    def update(self, instance, validated_data):
        validated_data.pop('img_cover', None)

        request = self.context.get('request')
        house = super().update(instance, validated_data)

        if request.data.getlist('disable_days'):
            house.disable_days.clear()

            for date in request.data.getlist('disable_days'):
                date_instance, created = HouseDisableDay.objects.get_or_create(date=date)
                house.disable_days.add(date_instance)

        if request.FILES:
            if request.data.get('img_cover'):
                clear_imagekit_cache()
                house.img_cover.delete()
                for img_cover in request.data.getlist('img_cover'):
                    house.img_cover.save(img_cover.name, img_cover)

            if request.data.get('house_images'):
                if house.images:
                    house.images.all().delete()

                for room_image in request.data.getlist('house_images'):
                    house.images.create_image(image=room_image)
        return house
