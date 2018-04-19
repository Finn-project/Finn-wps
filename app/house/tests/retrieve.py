import datetime
import os
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from utils.image.file import upload_file_cmp
from utils.image.resize import clear_imagekit_test_files
from ..models import Amenities, Facilities, House, HouseDisableDay, HouseImage

__all__ = (
    'HouseRetrieveTest',
)

User = get_user_model()


class HouseRetrieveTest(APITestCase):
    URL = '/house/'
    HOUSE_PK = 7

    HOUSE_COUNT = 13
    PAGE_SIZE = 3

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
        'latitude': '12.12345670000000',
        'longitude': '123.12345670000000',
    }

    def setUp(self):
        test_user_data1 = {
            'username': 'test01@gmail.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'first_name': '수민',
            'last_name': '박',
            'phone_num': '010123456789',
        }
        test_user_data2 = {
            'username': 'test02@gmail.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'first_name': '보영',
            'last_name': '박',
            'phone_num': '01099874456',
        }
        self.user1 = User.objects.create_django_user(**test_user_data1)
        self.user2 = User.objects.create_django_user(**test_user_data2)

        [Amenities.objects.create(name=name) for name in self.AMENITIES_LIST]
        [Facilities.objects.create(name=name) for name in self.FACILITIES_LIST]

        for i in range(self.HOUSE_COUNT):
            self.DATA['host'] = self.user1 if i % 2 else self.user2

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

    def test_retrieve_house(self):
        response = self.client.get(self.URL + f'{self.HOUSE_PK}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['pk'], self.HOUSE_PK)
        self.assertEqual(response.data['house_type'], self.DATA['house_type'])
        self.assertEqual(response.data['name'], self.DATA['name'])
        self.assertEqual(response.data['description'], self.DATA['description'])
        self.assertEqual(response.data['room'], self.DATA['room'])
        self.assertEqual(response.data['bed'], self.DATA['bed'])
        self.assertEqual(response.data['bathroom'], self.DATA['bathroom'])
        self.assertEqual(response.data['personnel'], self.DATA['personnel'])
        self.assertEqual(response.data['amenities'], self.AMENITIES)
        self.assertEqual(response.data['facilities'], self.FACILITIES)
        self.assertEqual(response.data['minimum_check_in_duration'], self.DATA['minimum_check_in_duration'])
        self.assertEqual(response.data['maximum_check_in_duration'], self.DATA['maximum_check_in_duration'])
        self.assertEqual(response.data['maximum_check_in_range'], self.DATA['maximum_check_in_range'])
        self.assertEqual(response.data['price_per_night'], self.DATA['price_per_night'])
        self.assertEqual(response.data['created_date'], datetime.date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['modified_date'], datetime.date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data.get('host').get('pk'),
                         self.user1.pk if (self.HOUSE_PK - 1) % 2 else self.user2.pk)
        self.assertEqual(response.data['country'], self.DATA['country'])
        self.assertEqual(response.data['city'], self.DATA['city'])
        self.assertEqual(response.data['district'], self.DATA['district'])
        self.assertEqual(response.data['dong'], self.DATA['dong'])
        self.assertEqual(response.data['address1'], self.DATA['address1'])
        # self.assertEqual(response.data['address2'], self.DATA['address2'])
        self.assertEqual(response.data['latitude'], self.DATA['latitude'])
        self.assertEqual(response.data['longitude'], self.DATA['longitude'])

        self.assertIsNotNone(response.data['disable_days'], 'disable_days')
        for index, date in enumerate(response.data['disable_days']):
            self.assertEqual(date.strftime('%Y-%m-%d'), self.DISABLE_DAYS[index])

        house = House.objects.get(pk=response.data['pk'])
        self.assertEqual(house.pk, self.HOUSE_PK)
        self.assertEqual(house.house_type, self.DATA['house_type'])
        self.assertEqual(house.name, self.DATA['name'])
        self.assertEqual(house.description, self.DATA['description'])
        self.assertEqual(house.room, self.DATA['room'])
        self.assertEqual(house.bed, self.DATA['bed'])
        self.assertEqual(house.bathroom, self.DATA['bathroom'])
        self.assertEqual(house.personnel, self.DATA['personnel'])
        self.assertEqual(list(house.amenities.values_list('pk', flat=True)), self.AMENITIES)
        self.assertEqual(list(house.facilities.values_list('pk', flat=True)), self.FACILITIES)
        self.assertEqual(house.minimum_check_in_duration, self.DATA['minimum_check_in_duration'])
        self.assertEqual(house.maximum_check_in_duration, self.DATA['maximum_check_in_duration'])
        self.assertEqual(house.maximum_check_in_range, self.DATA['maximum_check_in_range'])
        self.assertEqual(house.price_per_night, self.DATA['price_per_night'])
        self.assertEqual(house.created_date, datetime.date.today())
        self.assertEqual(house.modified_date, datetime.date.today())
        self.assertEqual(house.host.pk,
                         self.user1.pk if (self.HOUSE_PK - 1) % 2 else self.user2.pk)
        self.assertEqual(house.country, self.DATA['country'])
        self.assertEqual(house.city, self.DATA['city'])
        self.assertEqual(house.district, self.DATA['district'])
        self.assertEqual(house.dong, self.DATA['dong'])
        self.assertEqual(house.address1, self.DATA['address1'])
        # self.assertEqual(house.address2, self.DATA['address2'])
        self.assertEqual(house.latitude, Decimal(self.DATA['latitude']))
        self.assertEqual(house.longitude, Decimal(self.DATA['longitude']))

        self.assertEqual(house.disable_days.count(), len(self.DISABLE_DAYS))
        disable_day_list = list(house.disable_days.values_list('date', flat=True))
        for index, date in enumerate(disable_day_list):
            self.assertEqual(date.strftime('%Y-%m-%d'), self.DISABLE_DAYS[index])

        self.assertTrue(upload_file_cmp(file_path=self.file_path, img_name=house.img_cover.name))
        self.assertTrue(upload_file_cmp(file_path=self.house_image1_path, img_name=house.images.first().image.name))
        self.assertTrue(upload_file_cmp(file_path=self.house_image2_path, img_name=house.images.last().image.name))

        clear_imagekit_test_files()