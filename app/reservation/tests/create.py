import os
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import get_object_or_404

from utils.image.resize import clear_imagekit_test_files
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from house.models import House, Amenities, Facilities, HouseDisableDay, HouseImage

User = get_user_model()


class ReservationCreateTest(APITestCase):

    URL = '/reservation/'

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
    DATA = {
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
        self.DATA['host'] = self.host_user

        # HouseSerializer의 create method를 거치지 않고,
        #   바로 DB에서 house를 생성시키때문에 위에서 DATA안에 host를 넣어준 것.
        house = House.objects.create(**self.DATA)

        for amenity in self.AMENITIES:
            house.amenities.add(amenity)

        for facility in self.FACILITIES:
            house.facilities.add(facility)

        for disable_day in self.DISABLE_DAYS:
            date_instance, created = HouseDisableDay.objects.get_or_create(date=disable_day)
            house.disable_days.add(date_instance)

        self.file_path = os.path.join(settings.STATIC_DIR, 'iu.jpg')
        self.house_image1_path = os.path.join(settings.STATIC_DIR, 'test', 'test_inner_image.jpg')
        self.house_image2_path = os.path.join(settings.STATIC_DIR, 'test', 'test_outer_image.jpg')

        img_cover = open(self.file_path, 'rb')
        house_image1 = open(self.house_image1_path, 'rb')
        house_image2 = open(self.house_image2_path, 'rb')

        house.img_cover.save('iu.jpg', img_cover)
        houseimage1 = HouseImage.objects.create(house=house)
        houseimage2 = HouseImage.objects.create(house=house)
        houseimage1.image.save('test_inner_image.jpg', house_image1)
        houseimage2.image.save('test_outer_image.jpg', house_image2)

        img_cover.close()
        house_image1.close()
        house_image2.close()

    def test_create_reseration(self):

        # # Reservation 생성

        # 1) guest의 token값 client에 넣기
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token2.key,
        )

        # 2) 예약 관련 데이터 세팅
        now = timezone.now()
        check_in_date = (now + timedelta(1)).strftime('%Y-%m-%d')
        check_out_date = (now + timedelta(2)).strftime('%Y-%m-%d')
        data = {
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'house': 1,
            'guest_num': 3,
        }

        # 3) post 요청으로 예약 생성
        response = self.client.post(self.URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['check_in_date'], data['check_in_date'])
        self.assertEqual(response.data['check_out_date'], data['check_out_date'])
        self.assertEqual(response.data['guest_num'], 3)
        self.assertEqual(response.data['reservation_status'], 'RE')
        self.assertEqual(response.data['reservation_current_state'], 'BE')
        self.assertEqual(response.data['created_date'], timezone.now().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['modified_date'], timezone.now().strftime('%Y-%m-%d'))

        clear_imagekit_test_files()
