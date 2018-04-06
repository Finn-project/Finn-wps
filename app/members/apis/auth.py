from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import UserSerializer


class UserLoginAuthTokenAPIView(APIView):
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)


class UserLogoutView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response('해당 유저가 로그아웃되었습니다.', status=status.HTTP_200_OK)


class UserGetAuthTokenView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class IsUserHostAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request):
        if request.user.is_host:
            return Response('숙소를 등록한 호스트입니다.', status=status.HTTP_302_FOUND)
        return Response('숙소를 아직 등록하지 않은 게스트입니다.', status=status.HTTP_404_NOT_FOUND)