from django.contrib.auth import get_user_model
from rest_framework import serializers

from members.serializers import UserProfileImagesSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    images = UserProfileImagesSerializer(many=True)

    # images = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='img_profile',
    # )

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
