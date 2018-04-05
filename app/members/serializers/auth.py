from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from django.contrib.auth.password_validation import validate_password

from members.models import SIGNUP_TYPE_CHOICES, SIGNUP_TYPE_EMAIL
from utils.Exception.CustomException import CustomException

User = get_user_model()


class UserCreateSerializer(serializers.Serializer):
    """
    회원가입 절차에 필요한 인증절차를 가진 Serializer 새로 작성
    """
    email = serializers.EmailField(allow_null=True)
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    img_profile = serializers.ImageField(required=False)
    phone_num = serializers.CharField(required=False)
    signup_type = serializers.ChoiceField(choices=SIGNUP_TYPE_CHOICES, default=SIGNUP_TYPE_EMAIL)

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
        phone_num = attrs.get('phone_num')
        # img_profile = attrs.get('img_profile')

        if password and confirm_password:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_num=phone_num,
                signup_type=SIGNUP_TYPE_EMAIL,
                # img_profile=img_profile,
            )
            attrs['user'] = user

        return attrs


class UserUpdateSerializer(serializers.Serializer):
    """
    회원정보 수정 과정 중 필요한 인증절차를 가진 Serializer 새로 작성
    """
    email = serializers.EmailField(allow_null=True)
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_num = serializers.CharField(required=False)
    # img_profile = serializers.ImageField(required=False)

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

    def update(self, user, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        phone_num = attrs.get('phone_num', '')
        # img_profile = attrs.get('img_profile', '')

        if password and confirm_password:
            user.username = email
            user.email = email
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.phone_num = phone_num
            # user.img_profile = img_profile
            user.signup_type = SIGNUP_TYPE_EMAIL
            user.save()
            attrs['user'] = user

        return attrs
