from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404

from utils.pagination.custom_generic_pagination import DefaultPagination
from utils.permission.custom_permission import IsGuestOrReadOnly
from ..models import Reservation, House
from ..serializers import ReservationSerializer, ReservationPatchSerializer

__all__ = (
    'ReservationCreateListView',
    'ReservationRetrieveUpdateDestroyView',
)


class ReservationCreateListView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = DefaultPagination

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsGuestOrReadOnly,
    )

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
    serializer_class = ReservationSerializer
    pagination_class = DefaultPagination

    permission_classes = (
        permissions.IsAuthenticated,
        IsGuestOrReadOnly,
    )

    # def get_serializer_class(self):
    #     if self.request.method == 'PATCH':
    #         return ReservationPatchSerializer
    #     else:
    #         return ReservationSerializer

    def perform_update(self, serializer):
        super().perform_update(serializer)

    # def partial_update(self, request, *args, **kwargs):
    #     super().partial_update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
