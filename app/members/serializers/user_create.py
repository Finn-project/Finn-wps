from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers, status
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework.fields import ImageField

from members.serializers import UserProfileImagesSerializer, UserSerializer
from utils.exception.custom_exception import CustomException

User = get_user_model()

__all__ = (
    'UserCreateSerializer',
)


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    # images = UserProfileImagesSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'phone_num',
            # 'images',
        )

    def validate_username(self, username):
        # if User.objects.filter(username=username).exists():
        if User.objects.filter(Q(username=username) | Q(email=username)).exists():
            # Facebook으로 가입한 유저가 email 주소를 입력할 경우 위 쿼리문에서 에외처리를 하지 못해서
            # UNIQUE constraint failed: members_user.email 에러가 발생
            raise CustomException(detail='이미 존재하는 메일주소 입니다.', status_code=status.HTTP_409_CONFLICT)

        return username

    def validate_password(self, password):
        confirm_password = self.initial_data.get('confirm_password')
        errors = dict()

        if password != confirm_password:
            raise CustomException(detail='비밀번호가 일치하지 않습니다.', status_code=status.HTTP_400_BAD_REQUEST)

        if password.lower() in self.initial_data['username'].lower() or self.initial_data['username'].lower() in password.lower():
            raise CustomException(detail='아이디와 비밀번호는 유사하게 설정할 수 없습니다.', status_code=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password=password)
        except ValidationError as e:
            errors['detail'] = list(e.messages)
            raise CustomException(errors, status_code=status.HTTP_400_BAD_REQUEST)

        return password

    # def validate(self, attrs):
    #     if self.initial_data.get('img_profile'):
    #         images = self.initial_data['img_profile']
    #
    #         # restframework 내부 이미지 검증 코드 가져옴
    #         imf = ImageField()
    #         images2 = imf.to_internal_value(images)
    #
    #         attrs['images'] = images2

    def create(self, validated_data):
        # test_data = self.initial_data.get('img_profile')
        # test_data = self.initial_data.getlist('img_profile')
        # print(test_data)
        # print(validated_data)
        # print(*validated_data)
        # print(**validated_data)

        # return self.Meta.model.objects.create_django_user(test_data, validated_data)
        # 4/13 Postman 'raw' 형식으로 send 했을 때 self.initial_data.getlist('images')에서
        #      getlist를 할 경우 에러 발생 (get으로 하면 에러가 발생x, 'form-data'형식으로 보내도 에러x 원인은 모름)

        return User.objects.create_django_user(**validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # print(ret)

        token, _ = Token.objects.get_or_create(user=instance)
        data = {
            "token": token.key,
            "user": UserSerializer(instance).data,
        }
        return data
