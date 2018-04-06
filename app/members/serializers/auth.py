from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from rest_framework import serializers, status
from django.contrib.auth.password_validation import validate_password

from members.models import SIGNUP_TYPE_EMAIL, SIGNUP_TYPE_FACEBOOK
from utils.Exception.CustomException import CustomException

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    회원가입 절차에 필요한 인증절차를 가진 Serializer 새로 작성
    """
    # email = serializers.EmailField(allow_null=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    # first_name = serializers.CharField()
    # last_name = serializers.CharField()
    # phone_num = serializers.CharField(required=False)
    # img_profile = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'confirm_password',
            'email',
            'first_name',
            'last_name',
            'phone_num',
            'signup_type',
            'img_profile',
        )

    def validate_email(self, email):
        if User.objects.filter(username=email).exists():
            raise CustomException(detail='이미 존재 하는 메일주소 입니다.', status_code=status.HTTP_409_CONFLICT)

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

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data.get('email', ''),
            password=validated_data.get('password'),
            confirm_password=validated_data.get('confirm_password'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone_num=validated_data.get('phone_num', ''),
            signup_type=validated_data.get('phone_num', ''),
        )

        # default profile_image 생성
        # file = open('../.static/img_profile_default.png', 'rb').read()
        # user.img_profile.save('img_profile.png', ContentFile(file))

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    회원정보 수정 과정 중 필요한 인증절차를 가진 Serializer 새로 작성
    """
    # email = serializers.EmailField(allow_null=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    # first_name = serializers.CharField()
    # last_name = serializers.CharField()
    # phone_num = serializers.CharField(required=False)
    # img_profile = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'phone_num',
            'img_profile',
        )

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
        img_profile = attrs.get('img_profile')
        print(img_profile)

        if password and confirm_password:
            if not user.signup_type == SIGNUP_TYPE_FACEBOOK:
                user.username = email
            user.email = email
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.phone_num = phone_num
            user.signup_type = SIGNUP_TYPE_EMAIL
            if img_profile:
                print('프로필사진 업데이트한다')
                user.img_profile.save('img_profile.png', img_profile)
            user.save()
            attrs['user'] = user

        return attrs
