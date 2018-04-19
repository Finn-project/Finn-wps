from rest_framework import serializers

from members.models import UserProfileImages


class UserProfileImagesSerializer(serializers.ModelSerializer):

    img_profile_28 = serializers.ImageField(read_only=True)
    img_profile_225 = serializers.ImageField(read_only=True)
    img_profile = serializers.ImageField(use_url=True)

    class Meta:
        model = UserProfileImages
        fields = (
            # 'id',
            # 'user',
            'img_profile_28',
            'img_profile_225',
            'img_profile'
        )
