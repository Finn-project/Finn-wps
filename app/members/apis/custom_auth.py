from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.compat import authenticate

User = get_user_model()


class AuthTokenSerializerForFacebookUser(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):

        # 'user' 객체를 꺼내는 과정에서 발생하는 Exception을 아래처럼 raise하는 것보다
        # 이 전체 과정 자체를 email user의 AuthTokenSerailizing 과정보다 앞에서 두고
        # try ~ except 문으로 감싸는 방법을 사용해서 기존의 모든 Exception이 정상
        # 작동하도록 함.
        # try:
        email = attrs.get('username')
        user = User.objects.get(email=email)
        username = user.username
        # except:
        #     raise CustomException(detail='계정이 존재 하지 않습니다.', status_code=status.HTTP_409_CONFLICT)

        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
