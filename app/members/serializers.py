from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    signup_type = serializers.CharField(source='get_signup_type_display')

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'signup_type',
        )


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def check_request(self, *args, **kwargs):
        if User.objects.filter(username=kwargs.get('email')).exists():
            raise serializers.ValidationError('이미 존재 하는 메일 입니다.')

        if kwargs.get('password') != kwargs.get('confirm_password'):
            raise serializers.ValidationError('비밀번호가 일치하지 않습니다.')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')

        if password and confirm_password:
            self.check_request(email=email, password=password, confirm_password=confirm_password)
            
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                signup_type=User.SIGNUP_TYPE_EMAIL,
            )

        attrs['user'] = user
        return attrs
