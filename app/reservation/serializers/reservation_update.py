from datetime import timedelta

from django.db.models import Q
from rest_framework import status
from rest_framework.generics import get_object_or_404

from house.models import House, HouseReserveDay
from reservation.serializers import ReservationSerializer
from utils.exception.custom_exception import CustomException

__all__ = (
    'ReservationUpdateSerializer',
)


class ReservationUpdateSerializer(ReservationSerializer):

    def validate(self, attrs):

        if self.initial_data.get('house'):
            house_pk = self.initial_data.get('house')
            house = get_object_or_404(House, pk=house_pk)
            attrs['house'] = house
            # attrs에 'house' 객체를 넣어주면 def update() 에서 기존 'house'를
            # 업데이트 하게 된다.
        else:
            # Patch 예외처리 (1)
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
        reservation_instance = house.reservation_set.filter(~Q(pk=self.instance.pk))
        # Put / Patch일 경우(2) - 자신의 예약은 예외처리에서 제외

        for i in reservation_instance:
            staying_days = i.check_out_date - i.check_in_date
            reserved_days += [i.check_in_date + timedelta(n) for n in range(staying_days.days + 1)]

        # 기존 disable_days + 예약일
        disabled_and_reserved_days = disabled_days + reserved_days

        # check_in_date & check_out_date 기본 validation
        check_in_date = attrs.get('check_in_date', self.instance.check_in_date)
        check_out_date = attrs.get('check_out_date', self.instance.check_out_date)
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

        print(len(HouseReserveDay.objects.all()))
        HouseReserveDay.objects.filter(houses_with_reserve_day=None).delete()
        # .clear()로 ManyToMany 연결이 해제된 뒤 다시 연결되지 않은 object는 삭제
        print(len(HouseReserveDay.objects.all()))

        return r

    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     return ReservationSerializer(instance).data
