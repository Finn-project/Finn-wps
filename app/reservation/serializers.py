from rest_framework import serializers

from members.serializers import UserSerializer
from reservation.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):

    house = UserSerializer(read_only=True)
    guest = UserSerializer(read_only=True)

    class Meta:
        model = Reservation
        field = (
            'check_in_date',
            'check_out_date',
            'guest_num',
            'bank_account',
            'house',
            'guest',
            'created_date',
            'modified_date',
        )

