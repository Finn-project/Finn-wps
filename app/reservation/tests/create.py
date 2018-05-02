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

from house.models import House, Amenities, Facilities

User = get_user_model()


class ReservationAPITest(APITestCase):

    URL1 = '/house/'
    URL2 = '/reservation/'

    USERNAME = 'test1@gmail.com'
    PASSWORD = 'testpassword1'
    FIRST_NAME = '보영'
    LAST_NAME = '박'
    PHONE_NUM = '01012345567'

    USERNAME2 = 'test2@gmail.com'
    PASSWORD2 = 'testpassword2'
    FIRST_NAME2 = '이유'
    LAST_NAME2 = '아'
    PHONE_NUM2 = '01012345567'

    def setUp(self):
        # Host User 생성
        self.host_user = User.objects.create_user(
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        self.token, _ = Token.objects.get_or_create(user=self.host_user)

        # Guest User 생성
        # self.guest_user = User.objects.create_user(
        #     username=self.USERNAME2,
        #     password=self.PASSWORD2,
        # )
        # self.token2, _ = Token.objects.get_or_create(user=self.guest_user)

    def test_create_reseration(self):

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key,
        )
        file_path = os.path.join(settings.STATIC_DIR, 'iu.jpg')
        img_cover = open(file_path, 'rb')

        house_image1_path = os.path.join(settings.STATIC_DIR, 'test', 'test_inner_image.jpg')
        house_image2_path = os.path.join(settings.STATIC_DIR, 'test', 'test_outer_image.jpg')

        house_image1 = open(house_image1_path, 'rb')
        house_image2 = open(house_image2_path, 'rb')

        amenities_list = ['TV', '에어컨', '전자렌지', '커피포트', '컴퓨터', '공기청정기']
        facilities_list = ['수영장', '엘리베이터', '세탁소', '노래방', '오락실', '온천']

        [Amenities.objects.create(name=name) for name in amenities_list]
        [Facilities.objects.create(name=name) for name in facilities_list]

        data = {
            'house_type': House.HOUSE_TYPE_HOUSING,
            'name': '우리집',
            'description': '테스트용 집입니다.',
            'room': 1,
            'bed': 2,
            'bathroom': 2,
            'personnel': 3,
            'amenities': [],
            'facilities': [1, 2, 3, 4, 5],
            'minimum_check_in_duration': 1,
            'maximum_check_in_duration': 3,
            'maximum_check_in_range': 90,
            'price_per_night': 100000,
            'country': '대한민국',
            'city': '사랑시',
            'district': '고백구',
            'dong': '행복동',
            'address1': '777-1',
            # 'address2': '희망빌라 2동 301호',
            'latitude': '12.12345670000000',
            'longitude': '123.12345670000000',
            'disable_days': [
                '2014-01-01',
                '2014-02-01',
                '2014-03-01',
                '2014-04-01',
            ],
            'img_cover': img_cover,
            'house_images': [
                house_image1,
                house_image2,
            ],
        }

        response = self.client.post(self.URL1, data)
        house_pk = response.data.get('pk')
        house = get_object_or_404(House, pk=house_pk)

        # # Reservation 생성

        # 1) guest의 token값 client에 넣기
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key,
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
        response = self.client.post(self.URL2, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['check_in_date'], data['check_in_date'])
        self.assertEqual(response.data['check_out_date'], data['check_out_date'])
        self.assertEqual(response.data['guest_num'], 3)
        self.assertEqual(response.data['reservation_status'], 'RE')
        self.assertEqual(response.data['reservation_current_state'], 'BE')
        self.assertEqual(response.data['created_date'], timezone.now().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['modified_date'], timezone.now().strftime('%Y-%m-%d'))

        img_cover.close()
        house_image1.close()
        house_image2.close()
        clear_imagekit_test_files()
