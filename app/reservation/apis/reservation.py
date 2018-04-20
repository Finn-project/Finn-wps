from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from reservation.serializers.reservation_update import ReservationUpdateSerializer
from utils.pagination.custom_generic_pagination import DefaultPagination
from utils.permission.custom_permission import IsGuestOrReadOnly
from ..models import Reservation
from ..serializers import ReservationSerializer

__all__ = (
    'ReservationCreateListView',
    'ReservationRetrieveUpdateDestroyView',
)


# class ReservationFilter(django_filters.rest_framework.FilterSet):
#     house = django_filters.CharFilter(host="house__host")
#
#     class Meta:
#         model = Reservation
#         fields = ['guest', 'house']


class ReservationCreateListView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = DefaultPagination

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsGuestOrReadOnly,
    )

    filter_backends = (DjangoFilterBackend,)
    # filter_backends = (filters.OrderingFilter,)
    # filter_backends = (DjangoFilterBackend, filters.OrderingFilter)

    filter_fields = ('guest', 'house')
    # filter_fields = ('guest', 'house')
    # ordering_fields = ('pk', 'guest')
    # ordering = ('pk',)

    def perform_create(self, serializer):

        # house_pk = self.request.data.get('house')
        # house_instance = get_object_or_404(House, pk=house_pk)

        serializer.save(
            guest=self.request.user,
            # house=house_instance
        )

        # 아래 구문은 save() 두번 호출하는 중복구문.
        # super().perform_create(serializer)


class ReservationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationUpdateSerializer
    # pagination_class = DefaultPagination

    permission_classes = (
        permissions.IsAuthenticated,
        IsGuestOrReadOnly,
    )




    # def get_serializer_class(self):
    #     if self.request.method == 'PATCH':
    #         return ReservationPatchSerializer
    #     else:
    #         return ReservationSerializer

    # def perform_update(self, serializer):
    #     super().perform_update(serializer)

    def update(self, request, *args, **kwargs):
        result = super().update(request, *args, **kwargs)
        # UpdateModelMixin에서 리턴된 return Response(serializer.data)
        # 이 값이 왜 PUT / PATCH가 반영안된 데이터인지 의문.
        reservation_pk = kwargs['pk']
        reservation = Reservation.objects.get(pk=reservation_pk)

        return Response(ReservationSerializer(reservation).data)

    # def partial_update(self, request, *args, **kwargs):
    #     super().partial_update(request, *args, **kwargs)
    # -> 이 코드가 있을 때와 없을 때와 결과적으로 호출되는 프로세스는
    #    동일(?) 한 것 같은데 왜 Response를 돌려주지 않는 오류가 나는지 의문.

    # def perform_destroy(self, instance):
    #     super().perform_destroy(instance)
    #     return Response(해당 예약 삭제 되었습니다', status=status.HTTP_204_NO_CONTENT)
    # -> perform_destroy 하단에서 Response가 있기 때문에 바로 위의 Response가 호출이 안된것.

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        self.perform_destroy(instance)
        return Response('해당 예약이 삭제 되었습니다', status=status.HTTP_204_NO_CONTENT)
