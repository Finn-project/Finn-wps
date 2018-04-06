from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    signup_type = serializers.CharField(required=False)
    phone_num = serializers.CharField(required=False)
    img_profile = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'signup_type',
            'phone_num',
            'img_profile',
        )
