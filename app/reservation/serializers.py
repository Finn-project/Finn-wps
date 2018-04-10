from rest_framework import serializers

from reservation.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):

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

