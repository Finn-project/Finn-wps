from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..serializers import UserProfileImagesSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    images = UserProfileImagesSerializer()

    # images = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='img_profile',
    # )
    # 4/12 Trouble shooting - SlugRelatedField로 images 표현 불가

    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_num',
            'is_host',
            'is_email_user',
            'is_facebook_user',
            'images'
        )
