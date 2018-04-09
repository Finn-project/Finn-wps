from rest_framework import permissions, generics

from house.serializers.house_create import HouseCreateSerializer
from utils.pagination.custom_generic_pagination import DefaultPagination
from utils.permission.custom_permission import IsOwnerOrReadOnly
from ..serializers.house import HouseSerializer
from ..models import House

__all__ = (
    'HouseListCreateAPIView',
    'HouseRetrieveUpdateDestroyAPIView',
)


class HouseListCreateAPIView(generics.ListCreateAPIView):
    queryset = House.objects.all()
    serializer_class = HouseCreateSerializer
    pagination_class = DefaultPagination

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )

    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return HouseCreateSerializer
    #     elif self.request.method == 'GET':
    #         return HouseSerializer

    # def perform_create(self, serializer):
    #     house = serializer.save(host=self.request.user)
    #     house.amenities.set(self.request.data.getlist('amenities'))
    #     house.facilities.set(self.request.data.getlist('facilities'))
    #     house.save()
    def perform_create(self, serializer):
        # print('\nperform_create : ', self.request.data)
        super().perform_create(serializer)


class HouseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
