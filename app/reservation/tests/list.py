import os
from datetime import timedelta

import math
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import get_object_or_404

from reservation.models import Reservation
from reservation.serializers import ReservationSerializer
from utils.image.resize import clear_imagekit_test_files
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from house.models import House, Amenities, Facilities, HouseDisableDay, HouseImage

User = get_user_model()


class ReservationListTest(APITestCase):

    URL = '/reservation/'
    USER_COUNT = 7
    PAGE_SIZE = 3

    TEST_USER_DATA1 = {
        'username': 'test01@gmail.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword',
        'first_name': '이유',
        'last_name': '아',
        'phone_num': '010123456789',
    }
    TEST_USER_DATA2 = {
        'username': 'test02@gmail.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword',
        'first_name': '보영',
        'last_name': '박',
        'phone_num': '01099874456',
    }

    AMENITIES_LIST = ['TV', '에어컨', '전자렌지', '커피포트', '컴퓨터', '공기청정기']
    FACILITIES_LIST = ['수영장', '엘리베이터', '세탁소', '노래방', '오락실', '온천']

    AMENITIES = [1, 2, 3, 4]
    FACILITIES = [1, 2, 3]

    DISABLE_DAYS = [
        '2014-01-01',
        '2014-02-01',
        '2014-03-01',
        '2014-04-01',
    ]
    BASE_GPS = {
        'latitude': '37.55824700000000',
        'longitude': '126.92224100000000',
    }
    HOUSE_DATA = {
        'house_type': House.HOUSE_TYPE_HOUSING,
        'name': '우리집',
        'description': '테스트용 집입니다.',
        'room': 1,
        'bed': 2,
        'bathroom': 2,
        'personnel': 3,
        'minimum_check_in_duration': 1,
        'maximum_check_in_duration': 3,
        'maximum_check_in_range': 3,
        'price_per_night': 100000,
        'country': '대한민국',
        'city': '사랑시',
        'district': '고백구',
        'dong': '행복동',
        'address1': '777-1',
        # 'address2': '희망빌라 2동 301호',
        'latitude': BASE_GPS['latitude'],
        'longitude': BASE_GPS['longitude'],
    }

    def setUp(self):
        # Host User 생성
        self.host_user = User.objects.create_django_user(**self.TEST_USER_DATA1)
        self.token, _ = Token.objects.get_or_create(user=self.host_user)

        # Guest User 생성
        self.guest_user = User.objects.create_django_user(**self.TEST_USER_DATA2)
        self.token2, _ = Token.objects.get_or_create(user=self.guest_user)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key,
        )

        [Amenities.objects.create(name=name) for name in self.AMENITIES_LIST]
        [Facilities.objects.create(name=name) for name in self.FACILITIES_LIST]

        # house 생성 시 host_user 지정하기
        self.HOUSE_DATA['host'] = self.host_user

        # HouseSerializer의 create method를 거치지 않고,
        #   바로 DB에서 house를 생성시키때문에 위에서 DATA안에 host를 넣어준 것.
        self.house = House.objects.create(**self.HOUSE_DATA)

        for amenity in self.AMENITIES:
            self.house.amenities.add(amenity)

        for facility in self.FACILITIES:
            self.house.facilities.add(facility)

        for disable_day in self.DISABLE_DAYS:
            date_instance, created = HouseDisableDay.objects.get_or_create(date=disable_day)
            self.house.disable_days.add(date_instance)

        self.file_path = os.path.join(settings.STATIC_DIR, 'iu.jpg')
        self.house_image1_path = os.path.join(settings.STATIC_DIR, 'test', 'test_inner_image.jpg')
        self.house_image2_path = os.path.join(settings.STATIC_DIR, 'test', 'test_outer_image.jpg')

        img_cover = open(self.file_path, 'rb')
        house_image1 = open(self.house_image1_path, 'rb')
        house_image2 = open(self.house_image2_path, 'rb')

        self.house.img_cover.save('iu.jpg', img_cover)
        houseimage1 = HouseImage.objects.create(house=self.house)
        houseimage2 = HouseImage.objects.create(house=self.house)
        houseimage1.image.save('test_inner_image.jpg', house_image1)
        houseimage2.image.save('test_outer_image.jpg', house_image2)

        img_cover.close()
        house_image1.close()
        house_image2.close()

        # Reservation 생성
        for i in range(self.USER_COUNT):
            now = timezone.now()
            check_in_date = (now + timedelta(1 + i*2)).strftime('%Y-%m-%d')
            check_out_date = (now + timedelta(2 + i*2)).strftime('%Y-%m-%d')

            reservation_data = {
                'check_in_date': check_in_date,
                'check_out_date': check_out_date,
                'guest_num': 3,
                'guest': self.guest_user,
                'house': self.house,
            }
            reservation = Reservation.objects.create(**reservation_data)
            print(reservation)

    def test_create_reseration(self):

        page_num = math.ceil(self.USER_COUNT / self.PAGE_SIZE)

        for i in range(int(page_num)):
            response = self.client.get(self.URL, {'page': i + 1, 'page_size': self.PAGE_SIZE})

            # status code
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # count
            self.assertIsNotNone(response.data['count'], 'count')
            self.assertEqual(response.data['count'], self.USER_COUNT)

            # next, previous
            if i < page_num - 1:
                self.assertIsNotNone(response.data['next'])
            if i > 0:
                self.assertIsNotNone(response.data['previous'])

            # result
            # 1)
            # to_representation에서 build_absolute_uri() 때문에 위 assertEqual에서 fail

            # self.assertEqual(response.data['results'],
            #                  ReservationSerializer(
            #                      Reservation.objects.all()[i * self.PAGE_SIZE: (i + 1) * self.PAGE_SIZE],
            #                      many=True).data)
            # print(response.data['results'])
            # print(ReservationSerializer(
            #     Reservation.objects.all()[i * self.PAGE_SIZE:(i+1) * self.PAGE_SIZE], many=True).data)

            # 2)
            # adding url host
            reservation_object_list = []
            for i in ReservationSerializer(Reservation.objects.all()[i * self.PAGE_SIZE:(i+1) * self.PAGE_SIZE], many=True).data:

                i['house']['img_cover'] = 'http://testserver' + i['house']['img_cover']
                i['house']['img_cover_thumbnail'] = 'http://testserver' + i['house']['img_cover_thumbnail']

                for idx in range(len(i['house']['house_images'])):
                    i['house']['house_images'][idx] = 'http://testserver' + i['house']['house_images'][idx]
                reservation_object_list.append(i)

            print(reservation_object_list)
            self.assertEqual(response.data['results'], reservation_object_list)

        clear_imagekit_test_files()
