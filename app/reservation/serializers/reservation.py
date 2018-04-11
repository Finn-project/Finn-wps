from rest_framework import serializers

from house.serializers import HouseSerializer
from members.serializers import UserSerializer
from ..models import Reservation

__all__ = (
    'ReservationSerializer',
)


class ReservationSerializer(serializers.ModelSerializer):

    # house = HouseSerializer()
    guest = UserSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            'check_in_date',
            'check_out_date',
            'guest_num',
            'bank_account',
            'created_date',
            'modified_date',
            'house',
            'guest',
        )
        # fields = '__all__'
