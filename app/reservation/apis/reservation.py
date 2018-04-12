from rest_framework import generics, permissions

from utils.pagination.custom_generic_pagination import DefaultPagination
from ..models import Reservation, House
from ..serializers import ReservationSerializer

__all__ = (
    'ReservationCreateListView',
    'ReservationRetrieveUpdateDestroyView',
)


class ReservationCreateListView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        # IsGuestOrReadOnly,
    )

    pagination_class = DefaultPagination

    def perform_create(self, serializer):

        house_pk = self.request.data.get('house')
        house_instance, _ = House.objects.get_or_create(pk=house_pk)

        reservation = serializer.save(
            guest=self.request.user,
            house=house_instance
        )
        reservation.house = house_instance

        # 아래 구문은 save() 두번 호출하는 중복구문.
        # super().perform_create(serializer)


class ReservationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    pagination_class = DefaultPagination
