from django.contrib.auth import get_user_model
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from ..serializers import UserProfileImagesSerializer

User = get_user_model()


# class UserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
class UserSerializer(serializers.ModelSerializer):
    images = UserProfileImagesSerializer(read_only=True)

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

    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     print(ret)
    #
    #     token, _ = Token.objects.get_or_create(user=instance)
    #     data = {
    #         "token": token.key,
    #         "user": UserSerializer(instance).data,
    #     }
    #     return data
