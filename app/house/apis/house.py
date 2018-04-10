from rest_framework import permissions, generics

from utils.pagination.custom_generic_pagination import DefaultPagination
from utils.permission.custom_permission import IsOwnerOrReadOnly
from ..serializers import HouseSerializer, HouseCreateSerializer
from ..models import House

__all__ = (
    'HouseListCreateAPIView',
    'HouseRetrieveUpdateDestroyAPIView',
)


class HouseListCreateAPIView(generics.ListCreateAPIView):
    queryset = House.objects.all()
    # serializer_class = HouseSerializer
    pagination_class = DefaultPagination

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )

    def get_serializer_class(self):
        # 추후 하나로 합칠 예정
        if self.request.method == 'POST':
            return HouseCreateSerializer
        elif self.request.method == 'GET':
            return HouseSerializer

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

        self.request.user.is_host = True
        self.request.user.save()

        super().perform_create(serializer)


class HouseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = House.objects.all()
    # serializer_class = HouseSerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )

    def get_serializer_class(self):
        # 추후 하나로 합칠 예정
        if self.request.method == 'GET':
            return HouseCreateSerializer
        elif self.request.method == 'PUT':
            return HouseRetrieveUpdateDestroyAPIView
        elif self.request.method == 'PATCH':
            return HouseRetrieveUpdateDestroyAPIView(partial=True)
        elif self.request.method == 'DELETE':
            return HouseRetrieveUpdateDestroyAPIView

    def perform_update(self, serializer):
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
