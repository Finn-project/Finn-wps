from rest_framework import permissions, generics

from utils.pagination.custom_generic_pagination import DefaultPagination
from ..serializers.house import HouseSerializer
from ..models import House, Amenities, Facilities

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

    def perform_create(self, serializer):
        print(self.request.data['amenities'])
        print(self.request.data['facilities'])
        house = serializer.save(host=self.request.user)
        house.amenities.set(self.request.data['amenities'])
        house.facilities.set(self.request.data['facilities'])
        house.save()


class HouseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
