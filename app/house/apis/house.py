from django.db.models import Q
from rest_framework import permissions, generics, status
from rest_framework.response import Response

from utils.pagination.custom_generic_pagination import DefaultPagination
from utils.permission.custom_permission import IsHostOrReadOnly
from ..serializers import HouseSerializer
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
        IsHostOrReadOnly
    )

    def get_queryset(self):
        left_top_latitude = self.request.query_params.get('ltlatitude')
        left_top_longitude = self.request.query_params.get('ltlongitude')
        right_bottom_latitude = self.request.query_params.get('rblatitude')
        right_bottom_longitude = self.request.query_params.get('rblongitude')

        # 위도는 작고(lte) 크고(gte)
        # latitude <= left_top_latitude && latitude >= right_bottom_latitude
        # 경도는 크고(gte) 작고(lte)
        # longitude >= left_top_longitude && longitude <= right_bottom_longitude
        if left_top_latitude and left_top_longitude and right_bottom_latitude and right_bottom_longitude:
            houses = House.objects.filter(
                Q(latitude__lte=left_top_latitude), Q(latitude__gte=right_bottom_latitude),
                Q(longitude__gte=left_top_longitude), Q(longitude__lte=right_bottom_longitude),
            )
            return houses
        return House.objects.all()


class HouseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsHostOrReadOnly
    )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response('해당 숙소가 삭제 되었습니다', status=status.HTTP_204_NO_CONTENT)
