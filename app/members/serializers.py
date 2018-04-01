from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
        )


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')

        if email and password and confirm_password:
            user = authenticate(
                email=email,
                password=password,
                confirm_password=confirm_password,
                first_name=first_name,
                last_name=last_name,
            )

            if not user:
                raise serializers.ValidationError('인증에 실패 하셨습니다.', code='authorization')

        attrs['user'] = user
        return attrs
