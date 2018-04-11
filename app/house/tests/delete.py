from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from ..models import Amenities, Facilities, House

__all__ = (
    'HouseDeleteTest',
)

User = get_user_model()


class HouseDeleteTest(APITestCase):
    URL = '/house/'
    HOUSE_PK = 1

    AMENITIES_LIST = ['TV', '에어컨', '전자렌지', '커피포트', '컴퓨터', '공기청정기']
    FACILITIES_LIST = ['수영장', '엘리베이터', '세탁소', '노래방', '오락실', '온천']

    AMENITIES = [1, 2, 3, 4]
    FACILITIES = [1, 2, 3]

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
        'address2': '희망빌라 2동 301호',
        'latitude': '12.1234567',
        'longitude': '123.1234567',
    }

    def setUp(self):
        test_user_data = {
            'username': 'test01@gmail.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'first_name': '수민',
            'last_name': '박',
            'phone_num': '010123456789',
        }
        self.user = User.objects.create_django_user(**test_user_data)

        [Amenities.objects.create(name=name) for name in self.AMENITIES_LIST]
        [Facilities.objects.create(name=name) for name in self.FACILITIES_LIST]

        self.DATA['host'] = self.user

        house = House.objects.create(**self.DATA)

        for amenity in self.AMENITIES:
            house.amenities.add(amenity)

        for facility in self.FACILITIES:
            house.facilities.add(facility)

        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key,
        )

    def test_delete_house(self):
        response = self.client.delete(self.URL + f'{self.HOUSE_PK}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(House.objects.all())
