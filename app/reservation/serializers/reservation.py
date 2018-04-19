from datetime import timedelta

from django.db.models import Q
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404

from house.models import House, HouseReserveDay
from house.serializers import HouseSerializer
from members.serializers import UserSerializer
from utils.exception.custom_exception import CustomException
from ..models import Reservation

__all__ = (
    'ReservationSerializer',
)


class ReservationSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    # house = serializers.PrimaryKeyRelatedField(read_only=True)
    # house를 PrimaryKeyRelatedField로 하면 Response에서 tree 구조로 표현이 안되고 pk만 보임.
    house = HouseSerializer(read_only=True)
    guest = UserSerializer(read_only=True)
    reservation_current_state = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            'pk',
            'check_in_date',
            'check_out_date',
            'guest_num',
            'reservation_status',
            'reservation_current_state',
            'created_date',
            'modified_date',
            'guest',
            'house',
        )

    def validate(self, attrs):

        if self.initial_data.get('house'):
            # Put / Patch일 경우
            house_pk = self.initial_data.get('house')
            house = get_object_or_404(House, pk=house_pk)
            # house instance를 validated_data에 넣어주기
            # (pk로 house 값을 받았기 때문에 이 값을 인스턴스로 바꾸어주어야 한다.)
            attrs['house'] = house
            # attrs에 'house' 객체를 넣어주면 def update() 에서 기존 'house'를
            # 업데이트 하게 된다.
        elif self.instance:
            # Patch 예외처리
            house = self.instance.house
        else:
            # Create 예외처리 (1)
            raise CustomException(detail='house 정보가 입력되지 않았습니다.', status_code=status.HTTP_400_BAD_REQUEST)

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
            reservation_instance = house.reservation_set.filter(~Q(pk=self.instance.pk))
            # 업데이트 시 자신의 예약은 예외처리에서 제외
        else:
            # Reservation create 예외처리 (2)
            reservation_instance = house.reservation_set.filter()
        for i in reservation_instance:
            staying_days = i.check_out_date - i.check_in_date
            reserved_days += [i.check_in_date + timedelta(n) for n in range(staying_days.days + 1)]

        # 기존 disable_days + 예약일
        disabled_and_reserved_days = disabled_days + reserved_days

        if self.instance:
            check_in_date = attrs.get('check_in_date', self.instance.check_in_date)
            check_out_date = attrs.get('check_out_date', self.instance.check_out_date)
        else:
            # Reservation create 예외처리 (3)
            check_in_date = attrs.get('check_in_date')
            check_out_date = attrs.get('check_out_date')

        # Reservation create 예외처리 (4)
        if not check_in_date:
            raise CustomException(detail='check-in 정보가 입력되지 않았습니다.', status_code=status.HTTP_400_BAD_REQUEST)
        elif not check_out_date:
            raise CustomException(detail='check-out 정보가 입력되지 않았습니다.', status_code=status.HTTP_400_BAD_REQUEST)

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

    def create(self, validated_data):

        house = validated_data.get('house')

        r = super().create(validated_data)
        staying_days = r.check_out_date - r.check_in_date
        reserved_days = []
        reserved_days += [r.check_in_date + timedelta(n) for n in range(staying_days.days + 1)]

        for i in reserved_days:
            date_instance, _ = HouseReserveDay.objects.get_or_create(date=i)
            house.reserve_days.add(date_instance)

        return r

    def update(self, instance, validated_data):


        # house = validated_data.get('house')
        # PATCH의 경우 validated_data에 house 정보가 없을 수 있음
        house_pk = self.data.get('house').get('pk')
        house = get_object_or_404(House, pk=house_pk)
        house.reserve_days.clear()

        r = super().update(instance, validated_data)

        reserved_days = []
        reservations = house.reservation_set.all()
        for i in reservations:
            staying_days = i.check_out_date - i.check_in_date
            reserved_days += [i.check_in_date + timedelta(n) for n in range(staying_days.days + 1)]

        for j in reserved_days:
            date_instance, _ = HouseReserveDay.objects.get_or_create(date=j)
            house.reserve_days.add(date_instance)

        # 이 update 코드가 상단에 있어서 house obj에 연결된 reserve_days의 업데이트가 안된 상태로
        # 출력이 되고, 다음번 출력 값 또는 retrieve를 통해 이전번에 한 업데이트 내용을 보게 되었던 것

        # print(house.reserve_days.all())
        # print(HouseSerializer(house).data)
        #
        # print(len(HouseReserveDay.objects.all()))
        # HouseReserveDay.objects.filter(houses_with_reserve_day=None).delete()
        # print(len(HouseReserveDay.objects.all()))

        return r

    def get_reservation_current_state(self, obj):
        return obj.reservation_current_state

    # def to_representation(self, instance):
    #     return ReservationSerializer(instance).data
