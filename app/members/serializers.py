from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from django.contrib.auth.password_validation import validate_password

from utils.Exception.CustomException import CustomException

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    signup_type = serializers.CharField(source='get_signup_type_display')

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
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

    def validate_email(self, email):
        if User.objects.filter(username=email).exists():
            raise CustomException(detail='이미 존재 하는 메일 입니다.', status_code=status.HTTP_409_CONFLICT)

        return email

    def validate_password(self, password):
        confirm_password = self.initial_data.get('confirm_password')
        errors = dict()

        if password != confirm_password:
            raise CustomException(detail='비밀번호가 일치하지 않습니다.', status_code=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password=password)
        except ValidationError as e:
            errors['detail'] = list(e.messages)
            raise CustomException(errors, status_code=status.HTTP_400_BAD_REQUEST)

        return password

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')

        if password and confirm_password:
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


class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()

    def validate(self, attrs):
        access_token = attrs.get('access_token')
        if access_token:
            user = authenticate(access_token=access_token)
            if not user:
                raise CustomException(detail='페이스북 액세스 토큰이 올바르지 않습니다.', status_code=status.HTTP_401_UNAUTHORIZED)
        else:
            raise CustomException(detail='페이스북 액세스 토큰이 필요합니다.', status_code=status.HTTP_400_BAD_REQUEST)

        attrs['user'] = user
        return attrs
