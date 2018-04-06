from rest_framework import serializers, status
from rest_framework.compat import authenticate

from utils.exception.custom_exception import CustomException


class AccessTokenSerializer(serializers.Serializer):
    """
    페이스북 로그인 시 access_token의 인증절차를 추가한 Serializer 새로 작성
    """
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
