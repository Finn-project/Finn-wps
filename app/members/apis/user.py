from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    UserCreateSerializer,
    UserSerializer,
)

__all__ = (
    'UserListCreateAPIView',
    'UserRetrieveUpdateDestroyAPIView',
)

User = get_user_model()

"""
1. 유저만들기 (회원가입)
2. 유저리스트
3. 유저정보
4. 유저 삭제
5. 유저 수정
"""


class UserListCreateAPIView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)

    def get(self, request):
        user_list = [UserSerializer(user).data for user in User.objects.all()]
        return Response(user_list)


class UserRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request, pk):
        data = {
            'user': UserSerializer(get_object_or_404(User, pk=pk)).data
        }
        return Response(data)
    # get method로 pk값을 받는 위 함수의 경우 여러 이슈가 존재
    # 1. pk값을 클라이언트에서 알아야하는데 현재까지 딱히 pk값을 클라이언트에 전달하고 있지 않다.
    # 2. 위의 permission_classes때문에 auth-token값 까지 받는데
    #    auth-token값의 소유 사용자와 관계없이 pk를 넣은 유저정보가 return
    #    (물론 위 로직을 수정하면 되긴함..)
    # 3.apis/auth.py UserGetAuthTokenView가 pk 없이 똑같은 기능을 수행.

    def put(self, request):
        pass

    def delete(self, request):
        pass
