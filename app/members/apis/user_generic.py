from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from ..serializers import UserUpdateSerializer, UserSerializer, UserCreateSerializer
from utils.pagination.custom_generic_pagination import DefaultPagination
from utils.permission.custom_permission import IsOwnerOrReadOnly

User = get_user_model()

__all__ = (
    'UserListCreateView',
    'UserRetrieveUpdateDestroyView',
)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return UserCreateSerializer


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )
