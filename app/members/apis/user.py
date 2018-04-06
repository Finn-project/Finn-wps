from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer)

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
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)

    def get(self, request):
        """
        한페이지 당 25개
        """
        page_size = 25
        users = [UserSerializer(user).data for user in User.objects.filter(Q(is_superuser=False), Q(is_staff=False))]
        paginator = Paginator(users, page_size)

        page = request.GET.get('page')
        user_list = paginator.get_page(page).object_list
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

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk):
        # user = get_object_or_404(User, pk=pk)
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data.get('user')
            user.delete()
        return Response('해당 유저가 삭제되었습니다.', status=status.HTTP_204_NO_CONTENT)
