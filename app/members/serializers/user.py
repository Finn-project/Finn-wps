from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_num',
            'img_profile',
            'is_host',
            'is_email_user',
            'is_facebook_user',
        )
