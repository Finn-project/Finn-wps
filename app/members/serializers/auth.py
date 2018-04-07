from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import Q
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
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    username = serializers.EmailField(read_only=True)
    # username이 제대로 설정되었는지 확인하기 위해 read_only 옵션으로 출력만 되도록 설정
    #  Email user : email과 username이 동일하게 변경
    #  Facebook user : 기존의 username은 유지한 채 email만 변경
    email = serializers.EmailField(required=True)
    # Email, password을 무조건 받는 비지니스 로직(PUT Method 활용)을 설정하여 복잡함 제거
    # (페이스북 유저의 경우 회원정보 수정에서 이메일과 패스워드를 입력하지 않고 다른 회원정보만
    #  수정할 수도 있는데 이 경우 케이스가 하나 더 생기기 때문에 이 경우를 제외 한 것)

    is_email_user = serializers.BooleanField(read_only=True)
    is_facebook_user = serializers.BooleanField(read_only=True)
    # facebook user가 회원정보를 수정하게되면 is_email_user=True가 되는데
    # 이 부분이 바뀌었는지 확인하기 위해서 위에 read_only 옵션을 주고 출력되도록 함.

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
            'is_email_user',
            'is_facebook_user',
        )

    def validate_email(self, email):
        # 내 이 메일은 중복검사 하면 안되서 ~Q(username=self.instance) 추가
        if User.objects.filter(~Q(username=self.instance), Q(email=email)).exists():
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

    def update(self, user, validated_data):
        email = validated_data.get('email', user.email)
        password = validated_data.get('password', user.password)
        first_name = validated_data.get('first_name', user.first_name)
        last_name = validated_data.get('last_name', user.last_name)
        phone_num = validated_data.get('phone_num', user.phone_num)
        img_profile = validated_data.get('img_profile', '')
        print(img_profile)
        print(type(img_profile))

        # Facebook user의 경우에는 username과 email을 다르게 설정해야함.
        if user.is_facebook_user:
            # Facebook user도 메일주소를 가졌다는 것을 표시
            user.is_email_user = True
        else:
            user.username = email
        user.email = email
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.phone_num = phone_num
        user.save()
        # 유저가 사진을 삭제했을 경우 default 이미지로 다시 넣어준다.
        if img_profile == '':
            file = open('../.static/img_profile_default.png', 'rb').read()
            user.img_profile.save('img_profile.png', ContentFile(file))
        else:
            user.img_profile.save('img_profile.png', img_profile)

        return user
