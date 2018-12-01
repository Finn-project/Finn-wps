from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from members.serializers.facebook_auth import AuthTokenSerializerForFacebookUser
from ..serializers import UserSerializer


User = get_user_model()


class UserLoginAuthTokenAPIView(APIView):
    def post(self, request):
        # try:
        # 2018.12.01
        # Code refactoring with
        if User.objects.filter(email=request.POST['username']).exists():
            # Facebook user가 username이 아닌 email로 일반 Auth 로그인 시도하는
            # 케이스를 위한 AuthTokenSerializer 별도로 정의
            serializer = AuthTokenSerializerForFacebookUser(data=request.data)
            serializer.is_valid(raise_exception=True)
        # except ObjectDoesNotExist:
        else:
            # Facebook user 로그인이 실패할 경우 일반 로그인으로 진행
            serializer = AuthTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)


class UserLogoutAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response('해당 유저가 로그아웃되었습니다.', status=status.HTTP_204_NO_CONTENT)


class UserGetAuthTokenAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
