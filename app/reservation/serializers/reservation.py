from datetime import timedelta

from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404

from house.models import House
from house.serializers import HouseSerializer
from members.serializers import UserSerializer
from utils.exception.custom_exception import CustomException
from ..models import Reservation

__all__ = (
    'ReservationSerializer',
)


class ReservationSerializer(serializers.ModelSerializer):

    # house = serializers.PrimaryKeyRelatedField(read_only=True)
    # house를 PrimaryKeyRelatedField로 하면 Response에서 tree 구조로 표현이 안되고 pk만 보임.
    house = HouseSerializer(read_only=True)
    guest = UserSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            'pk',
            'check_in_date',
            'check_out_date',
            'guest_num',
            'reservation_status',
            'created_date',
            'modified_date',
            'guest',
            'house',
        )

    def validate(self, attrs):

        if self.initial_data.get('house'):
            house_pk = self.initial_data.get('house')
            house = get_object_or_404(House, pk=house_pk)
            # house instance를 validated_data에 넣어주기
            # (pk로 house 값을 받았기 때문에 이 값을 인스턴스로 바꾸어주어야 한다.)
            attrs['house'] = house
            # attrs에 'house' 객체를 넣어주면 def update() 에서 기존 'house'를
            # 업데이트 하게 된다.
        else:
            # raise CustomException(detail='house 정보가 입력되지 않았습니다.', status_code=status.HTTP_400_BAD_REQUEST)
            house = self.instance.house

        # 숙박 인원 validation
        if attrs.get('guest_num') and house.personnel < attrs['guest_num']:
            raise CustomException(detail='숙박 허용인원을 초과했습니다.', status_code=status.HTTP_400_BAD_REQUEST)

        # 기존 disable_days 찾기
        disabled_days = []
        for i in house.disable_days.all():
            disabled_days.append(i.date)

        # 기존 예약일 찾기
        reserved_days = []
        if self.instance:
            reserved_days_list = house.reservation_set.filter(~Q(pk=self.instance.pk))
            # 업데이트 시 자신의 예약은 예외처리에서 제외
        else:
            reserved_days_list = house.reservation_set.filter()
        for i in reserved_days_list:
            staying_days = i.check_out_date - i.check_in_date
            reserved_days += [i.check_in_date + timedelta(n) for n in range(staying_days.days + 1)]

        # 기존 disable_days + 예약일
        disabled_and_reserved_days = disabled_days + reserved_days

        check_in_date = attrs.get('check_in_date', self.instance.check_in_date)
        check_out_date = attrs.get('check_out_date', self.instance.check_out_date)

        # check_in_date & check_out_date 기본 validation
        if check_in_date > check_out_date or check_in_date == check_out_date:
            raise CustomException(detail='체크인, 체크아웃 날짜를 잘못 선택하셨습니다.', status_code=status.HTTP_400_BAD_REQUEST)

        # check_in_date & check_out_date 연관 validation
        for day in disabled_and_reserved_days:
            if day < check_in_date or day > check_out_date:
                pass
            else:
                raise CustomException(detail='예약할 수 없는 날짜를 선택하셨습니다.', status_code=status.HTTP_400_BAD_REQUEST)

        return attrs

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
