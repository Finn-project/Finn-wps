from rest_framework import permissions, generics

from utils.pagination.custom_generic_pagination import DefaultPagination
from ..serializers.house import HouseSerializer
from ..models import House

__all__ = (
    'HouseListCreateAPIView',
    'HouseRetrieveUpdateDestroyAPIView',
)


class HouseListCreateAPIView(generics.ListCreateAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    pagination_class = DefaultPagination

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )


class HouseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
