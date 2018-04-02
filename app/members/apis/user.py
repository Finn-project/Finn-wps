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

    def put(self, request):
        pass

    def delete(self, request):
        pass
