import os
import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from ..models import (
    House,
    Amenities,
    Facilities
)

__all__ = (
    'HouseCreateTest',
)

User = get_user_model()


class HouseCreateTest(APITestCase):
    URL = '/house/'

    def setUp(self):
        test_user_data = {
            'username': 'test@gmail.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'first_name': '수민',
            'last_name': '박',
            'phone_num': '010123456789',
        }
        self.user = User.objects.create_django_user(**test_user_data)
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_check_user(self):
        self.assertEqual(self.user.username, 'test@gmail.com')

    def test_create_house(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key,
        )
        # house_image1 = os.path.join(settings.STATIC_DIR, 'test', 'test_inner_image.jpg')
        # house_image2 = os.path.join(settings.STATIC_DIR, 'test', 'test_outer_image.jpg')

        amenities_list = ['TV', '에어컨', '전자렌지', '커피포트', '컴퓨터', '공기청정기']
        facilities_list = ['수영장', '엘리베이터', '세탁소', '노래방', '오락실', '온천']

        [Amenities.objects.create(name=name) for name in amenities_list]
        [Facilities.objects.create(name=name) for name in facilities_list]

        data = {
            'house_type': House.HOUSE_TYPE_HOUSING,
            'name': '우리집',
            'description': '테스트용 집입니다.',
            'room': 1,
            'bathroom': 2,
            'personnel': 3,
            'amenities': [1, 2, 3, 4, 5],
            'facilities': [1, 2, 3, 4, 5],
            'minimum_check_in_duration': 1,
            'maximum_check_in_duration': 3,
            # 'start_day_for_break': datetime.date(2018, 4, 1),
            # 'end_day_for_break': datetime.date(2018, 4, 15),
            'maximum_check_in_range': 3,
            'price_per_night': 100000,
            'created_date': datetime.datetime.today(),
            'modified_date': datetime.datetime.today(),
            # 'host': self.user.pk,
            'country': '대한민국',
            'city': '사랑시',
            'district': '고백구',
            'dong': '행복동',
            'address1': '777-1',
            'address2': '희망빌라 2동 301호',
            'latitude': 12.1234567,
            'longitude': 123.1234567,
        }

        print('test_create_house: ', data['amenities'])
        response = self.client.post(self.URL, data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
