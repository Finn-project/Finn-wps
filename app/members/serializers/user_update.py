from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers, status
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework.fields import ImageField

from members.serializers import UserProfileImagesSerializer, UserSerializer
from ..models import UserProfileImages
from utils.exception.custom_exception import CustomException

User = get_user_model()

__all__ = (
    'UserUpdateSerializer',
)


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
    # img_profile_thumbnail = serializers.ImageField(read_only=True)
    images = UserProfileImagesSerializer(read_only=True)

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
            'is_email_user',
            'is_facebook_user',

            'images',
        )

    def validate_email(self, email):
        # 내 이 메일은 중복검사 하면 안되서 ~Q(username=self.instance) 추가
        if User.objects.filter(~Q(username=self.instance.username), Q(email=email)).exists():
            raise CustomException(detail='이미 존재 하는 메일주소 입니다.', status_code=status.HTTP_409_CONFLICT)

        return email

    def validate_password(self, password):
        confirm_password = self.initial_data.get('confirm_password')
        errors = dict()

        if password != confirm_password:
            raise CustomException(detail='비밀번호가 일치하지 않습니다.', status_code=status.HTTP_400_BAD_REQUEST)

        # Patch 예외처리
        if self.initial_data.get('username'):
            username = self.initial_data.get('username')
        else:
            username = self.instance.username

        if password.lower() in username.lower() or username.lower() in password.lower():
            raise CustomException(detail='아이디와 비밀번호는 유사하게 설정할 수 없습니다.', status_code=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password=password)
        except ValidationError as e:
            errors['detail'] = list(e.messages)
            raise CustomException(errors, status_code=status.HTTP_400_BAD_REQUEST)

        return password

    def validate(self, attrs):
        if self.initial_data.get('img_profile'):
            images = self.initial_data['img_profile']

            # restframework 내부 이미지 검증 코드 가져옴
            imf = ImageField()
            images2 = imf.to_internal_value(images)

            attrs['images'] = images2

        return attrs

    def update(self, user, validated_data):
        email = validated_data.get('email', user.email)
        # password = validated_data.get('password', user.password)
        # 회원정보 수정을 PUT -> PATCH로 바꾸면서 예외처리를 위해 변경
        password = validated_data.get('password', '')
        first_name = validated_data.get('first_name', user.first_name)
        last_name = validated_data.get('last_name', user.last_name)
        phone_num = validated_data.get('phone_num', user.phone_num)
        img_profile = validated_data.get('images')

        # Facebook user의 경우에는 username과 email을 다르게 설정해야함.
        if user.is_facebook_user:
            # Facebook user도 메일주소를 가졌다는 것을 표시
            user.is_email_user = True
        else:
            # email user의 경우에만 변경한 email과 username을 같도록 설정해준다.
            # -> signup_type 대신에 is_facebook_user / is_email_user로
            #    나누어야 하는 이유
            user.username = email
        user.email = email

        if password:
            user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.phone_num = phone_num
        user.save()

        if img_profile is None:
            # '' 값은 위의 img_profile = validated_data.get('img_profile', '')
            # 에서 img_profile 값이 입력되지 않았을 경우인데,
            # 이게 Postman 문제인지는 모르겠지만 null값을 보낼때와 빈 값('')을 보낼 때와
            # validated_data에 똑같이 아무 값도 들어오지 않기 때문에 두 경우를
            # 구분할 수 없는데 이 부분은 실제 프론트와의 파일 업로드 테스트에서도 동일한지
            # 확인할 필요가 있다.

            pass
            # 유저가 사진을 입력안한 경우 그냥둔다.

            # 저장소에 기존 이미지가 없을 경우 default 이미지를 넣어준다.
            # (* static 이미지를 활용하는 방법을 알아낼 경우 아래 코드 Refactoring 예정)
            # if user.img_profile:
            #     user.img_profile.delete()
            # 1) 이미지 경로 문제로 제외
            # static_storage_class = import_string(settings.STATICFILES_STORAGE)
            # static_storage = static_storage_class()
            # static_file = static_storage.open(
            #     'img_profile_default.png'
            # )
            # user.images.create(img_profile=static_file)

            # 2) 이미지 경로 제대로 들어감.
            # file = open('../.static/img_profile_default.png', 'rb').read()
            # img = UserProfileImages.objects.create(user=user)
            # img.img_profile.save('img_profile.png', ContentFile(file))

            # 3) 4/10 오전 미팅결과 iOS/FDS에서 Default image 세팅하기로 결론

        else:
            img, _ = UserProfileImages.objects.get_or_create(user=user)
            # UserProfileImages가 OneToOneField이기 때문에 기존
            # Foreignkey처럼 user.images.all().delete()한 다음
            # user.images에 접근할 수 없다.
            # Q. 기존 Foreignkey에서는 모든 연결된 객체가 삭제되었는데
            # user.images로 접근할 때 에러가 안난 이유는?

            # clear_imagekit_cache_img_profile(user, user.pk)
            # clear_imagekit_cache_img_profile(user.pk)
            if user.images.img_profile:
                user.images.img_profile.delete()
                user.images.img_profile_28.delete()
                user.images.img_profile_225.delete()

            # 1) 먼저 생각난 방법
            img.img_profile_28.save('img_profile_28.png', img_profile)
            img.img_profile_225.save('img_profile_225.png', img_profile)
            img.img_profile.save('img_profile.png', img_profile)

            # 2) 다른 방법
            # data = ContentFile(img_profile.read())
            # img.img_profile_28.save('img_profile_28.png', data)
            # img.img_profile_225.save('img_profile_225.png', data)
            # img.img_profile.save('img_profile.png', data)

        return user

    def to_representation(self, instance):
        # ret = super().to_representation(instance)

        token, _ = Token.objects.get_or_create(user=instance)
        return UserSerializer(instance).data
