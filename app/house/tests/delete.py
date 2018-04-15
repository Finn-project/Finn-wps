import os

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from utils.image.resize import clear_imagekit_test_files
from ..models import Amenities, Facilities, House, HouseImage

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

        self.file_path = os.path.join(settings.STATIC_DIR, 'iu.jpg')
        self.house_image1_path = os.path.join(settings.STATIC_DIR, 'test', 'test_inner_image.jpg')
        self.house_image2_path = os.path.join(settings.STATIC_DIR, 'test', 'test_outer_image.jpg')

        img_cover = open(self.file_path, 'rb')
        house_image1 = open(self.house_image1_path, 'rb')
        house_image2 = open(self.house_image2_path, 'rb')

        house.img_cover.save('iu.jpg', img_cover)
        house1 = HouseImage.objects.create(house=house)
        house2 = HouseImage.objects.create(house=house)
        house1.image.save('test_inner_image.jpg', house_image1)
        house2.image.save('test_outer_image.jpg', house_image2)

        img_cover.close()
        house_image1.close()
        house_image2.close()

        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key,
        )

    def test_delete_house(self):
        response = self.client.delete(self.URL + f'{self.HOUSE_PK}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(House.objects.all())

        self.assertEqual(HouseImage.objects.filter(house__pk=self.HOUSE_PK).count(), 0)
        clear_imagekit_test_files()