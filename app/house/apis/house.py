from rest_framework import permissions, generics, status
from rest_framework.response import Response

from utils.image.resize import clear_imagekit_cache
from utils.pagination.custom_generic_pagination import DefaultPagination
from utils.permission.custom_permission import IsHostOrReadOnly
from ..serializers import HouseSerializer, HouseCreateSerializer, HouseRetrieveUpdateDestroySerializer
from ..models import House, HouseDisableDay

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
        IsHostOrReadOnly
    )

    def get_serializer_class(self):
        # 추후 하나로 합칠 예정
        if self.request.method == 'POST':
            return HouseCreateSerializer
        elif self.request.method == 'GET':
            return HouseSerializer

    def perform_create(self, serializer):
        house = serializer.save(host=self.request.user)

        for date in self.request.data.getlist('disable_days'):
            date_instance, created = HouseDisableDay.objects.get_or_create(date=date)
            house.disable_days.add(date_instance)

        if self.request.FILES:
            for img_cover in self.request.data.getlist('img_cover'):
                house.img_cover.save(img_cover.name, img_cover)

            for room_image in self.request.data.getlist('house_images'):
                house.images.create(image=room_image)

        self.request.user.is_host = True
        self.request.user.save()


class HouseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = House.objects.all()
    # serializer_class = HouseRetrieveUpdateDestroySerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsHostOrReadOnly
    )

    def get_serializer_class(self):
        # 추후 하나로 합칠 예정
        if self.request.method == 'GET':
            return HouseSerializer
        return HouseRetrieveUpdateDestroySerializer

    def perform_update(self, serializer):
        house = serializer.save(host=self.request.user)

        if self.request.data.getlist('disable_days'):
            house.disable_days.clear()

            for date in self.request.data.getlist('disable_days'):
                date_instance, created = HouseDisableDay.objects.get_or_create(date=date)
                house.disable_days.add(date_instance)

        if self.request.data.get('img_cover'):
            clear_imagekit_cache()
            house.img_cover.delete()
            for img_cover in self.request.data.getlist('img_cover'):
                house.img_cover.save(img_cover.name, img_cover)

        if self.request.data.get('house_images'):
            if house.images:
                house.images.all().delete()

            for room_image in self.request.data.getlist('house_images'):
                house.images.create(image=room_image)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response('해당 숙소가 삭제 되었습니다', status=status.HTTP_204_NO_CONTENT)
