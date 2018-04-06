from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from rest_framework import serializers, status
from django.contrib.auth.password_validation import validate_password

from utils.exception.custom_exception import CustomException

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'phone_num',
        )

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise CustomException(detail='이미 존재 하는 메일주소 입니다.', status_code=status.HTTP_409_CONFLICT)

        return username

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
        return self.Meta.model.objects.create_django_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    회원정보 수정 과정 중 필요한 인증절차를 가진 Serializer 새로 작성
    """
    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username',
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

    # def update(self, user, attrs):
    #     username = attrs.get('username', user.username)
    #     email = attrs.get('email', username)
    #     password = attrs.get('password', user.password)
    #     first_name = attrs.get('first_name', user.first_name)
    #     last_name = attrs.get('last_name', user.last_name)
    #     phone_num = attrs.get('phone_num', user.phone_num)
    #     img_profile = attrs.get('img_profile')
    #
    #     user.username = username
    #     user.email = email
    #     user.set_password(password)
    #     user.first_name = first_name
    #     user.last_name = last_name
    #     user.phone_num = phone_num
    #     # user.signup_type = SIGNUP_TYPE_EMAIL
    #
    #     # 유저가 사진을 삭제했을 경우 default 이미지로 다시 넣어준다.
    #     if not img_profile:
    #         file = open('../.static/img_profile_default.png', 'rb').read()
    #         user.img_profile.save('img_profile.png', ContentFile(file))
    #     attrs['user'] = user
    #
    #     return attrs

    # 위 update 오버라이딩 코드가 'username'에서만 return Response(serializer.data)에서
    #   키에러가 발생해서 기존의 update 메소드를 사용하는 아래 코드로 변경.
    #   원인 모름..
    def update(self, user, attrs):
        attrs = super().update(user,attrs)

        # 현재 postman 테스트에서는 img_profile을 빈값으로 보내도 img_profile이
        # 빈값으로 채워지지 않고 기존 사진으로 유지됨 -> postman외 실제 테스트에서도 동일하게
        # 적용되는지 확인해보고, 만약 동일하면 별도의 프로필 사진 제거 기능 추가 필요.
        if not user.img_profile:
            file = open('../.static/img_profile_default.png', 'rb').read()
            user.img_profile.save('img_profile.png', ContentFile(file))

        return attrs
