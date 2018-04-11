from rest_framework import generics, permissions

from utils.pagination.custom_generic_pagination import DefaultPagination
from ..models import Reservation
from ..serializers import ReservationSerializer

__all__ = (
    'ReservationCreateListView',
    'ReservationRetrieveUpdateDestroyView',
)


class ReservationCreateListView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (
        permissions.IsAuthenticated
        # IsHostAndGuestOnly, 필요?
    )

    pagination_class = DefaultPagination


class ReservationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (
        permissions.IsAuthenticated
    )

    pagination_class = DefaultPagination
