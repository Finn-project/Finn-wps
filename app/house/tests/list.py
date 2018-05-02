import datetime
import math
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
    'HouseListTest',
)

User = get_user_model()


class HouseListTest(APITestCase):
    URL = '/house/'

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
            if i > 0:
                self.DATA['latitude'] = '35.21389421799400'
                self.DATA['longitude'] = '129.07717830846500'

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

    def test_list_house(self):
        page_num = math.ceil(self.HOUSE_COUNT / self.PAGE_SIZE)

        for i in range(int(page_num)):
            response = self.client.get(self.URL, {'page': i + 1, 'page_size': self.PAGE_SIZE})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertIsNotNone(response.data['count'], 'count')
            self.assertEqual(response.data['count'], self.HOUSE_COUNT)

            if i < page_num - 1:
                self.assertIsNotNone(response.data['next'], 'next')
            if i > 0:
                self.assertIsNotNone(response.data['previous'], 'previous')

            results = response.data['results']

            for j in range(len(results)):
                house_result = results[j]
                self.assertEqual(house_result['pk'], ((i * self.PAGE_SIZE) + j) + 1)
                self.assertEqual(house_result['house_type'], self.DATA['house_type'])
                self.assertEqual(house_result['name'], self.DATA['name'])
                self.assertEqual(house_result['description'], self.DATA['description'])
                self.assertEqual(house_result['room'], self.DATA['room'])
                self.assertEqual(house_result['bed'], self.DATA['bed'])
                self.assertEqual(house_result['bathroom'], self.DATA['bathroom'])
                self.assertEqual(house_result['personnel'], self.DATA['personnel'])
                self.assertEqual(house_result['amenities'], self.AMENITIES)
                self.assertEqual(house_result['facilities'], self.FACILITIES)
                self.assertEqual(house_result['minimum_check_in_duration'], self.DATA['minimum_check_in_duration'])
                self.assertEqual(house_result['maximum_check_in_duration'], self.DATA['maximum_check_in_duration'])
                self.assertEqual(house_result['maximum_check_in_range'], self.DATA['maximum_check_in_range'])
                self.assertEqual(house_result['price_per_night'], self.DATA['price_per_night'])
                self.assertEqual(house_result['created_date'], datetime.date.today().strftime('%Y-%m-%d'))
                self.assertEqual(house_result['modified_date'], datetime.date.today().strftime('%Y-%m-%d'))
                self.assertEqual(house_result.get('host').get('pk'),
                                 self.user1.pk if ((i * self.PAGE_SIZE) + j) % 2 else self.user2.pk)
                self.assertEqual(house_result['country'], self.DATA['country'])
                self.assertEqual(house_result['city'], self.DATA['city'])
                self.assertEqual(house_result['district'], self.DATA['district'])
                self.assertEqual(house_result['dong'], self.DATA['dong'])
                self.assertEqual(house_result['address1'], self.DATA['address1'])
                self.assertEqual(house_result['latitude'], self.BASE_GPS['latitude'] if i + j == 0 else self.DATA['latitude'])
                self.assertEqual(house_result['longitude'], self.BASE_GPS['longitude'] if i + j == 0 else self.DATA['longitude'])

                self.assertIn('disable_days', house_result)

                for index, date in enumerate(house_result['disable_days']):
                    self.assertEqual(date.strftime('%Y-%m-%d'), self.DISABLE_DAYS[index])

                self.assertIn('house_images', house_result)

                house = House.objects.get(pk=house_result['pk'])
                self.assertEqual(house.pk, ((i * self.PAGE_SIZE) + j) + 1)
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
                                 self.user1.pk if ((i * self.PAGE_SIZE) + j) % 2 else self.user2.pk)
                self.assertEqual(house.country, self.DATA['country'])
                self.assertEqual(house.city, self.DATA['city'])
                self.assertEqual(house.district, self.DATA['district'])
                self.assertEqual(house.dong, self.DATA['dong'])
                self.assertEqual(house.address1, self.DATA['address1'])
                # self.assertEqual(house.address2, self.DATA['address2'])
                self.assertEqual(house.latitude,
                                 Decimal(self.BASE_GPS['latitude']) if i + j == 0 else Decimal(self.DATA['latitude']))
                self.assertEqual(house.longitude,
                                 Decimal(self.BASE_GPS['longitude']) if i + j == 0 else Decimal(self.DATA['longitude']))

                self.assertEqual(house.disable_days.count(), len(self.DISABLE_DAYS))
                disable_day_list = list(house.disable_days.values_list('date', flat=True))
                for index, date in enumerate(disable_day_list):
                    self.assertEqual(date.strftime('%Y-%m-%d'), self.DISABLE_DAYS[index])

                self.assertTrue(upload_file_cmp(file_path=self.file_path, img_name=house.img_cover.name))
                self.assertTrue(
                    upload_file_cmp(file_path=self.house_image1_path, img_name=house.images.first().image.name))
                self.assertTrue(
                    upload_file_cmp(file_path=self.house_image2_path, img_name=house.images.last().image.name))

        clear_imagekit_test_files()

    def test_list_house_field_set(self):
        page_num = math.ceil(self.HOUSE_COUNT / self.PAGE_SIZE)

        for i in range(int(page_num)):
            response = self.client.get(self.URL, {'page': i + 1, 'page_size': self.PAGE_SIZE, 'fields': 'pk,name,latitude,longitude'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertIsNotNone(response.data['count'], 'count')
            self.assertEqual(response.data['count'], self.HOUSE_COUNT)

            if i < page_num - 1:
                self.assertIsNotNone(response.data['next'], 'next')
            if i > 0:
                self.assertIsNotNone(response.data['previous'], 'previous')

            results = response.data['results']

            for j in range(len(results)):
                house_result = results[j]
                self.assertEqual(house_result['pk'], ((i * self.PAGE_SIZE) + j) + 1)
                self.assertEqual(house_result['name'], self.DATA['name'])

                self.assertEqual(house_result['latitude'], self.BASE_GPS['latitude'] if i + j == 0 else self.DATA['latitude'])
                self.assertEqual(house_result['longitude'], self.BASE_GPS['longitude'] if i + j == 0 else self.DATA['longitude'])

                house = House.objects.get(pk=house_result['pk'])
                self.assertEqual(house.pk, ((i * self.PAGE_SIZE) + j) + 1)
                self.assertEqual(house.name, self.DATA['name'])

    def test_list_house_field_set_gps(self):
        response = self.client.get(self.URL, {
            'fields': 'pk,name,latitude,longitude',
            'ne_lat': 38.0,
            'ne_lng': 127.0,
            'sw_lat': 36.0,
            'sw_lng': 126.0,
            'ordering': '-pk',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsNotNone(response.data['count'], 'count')

        results = response.data['results']

        for j in range(len(results)):
            house_result = results[j]

            self.assertEqual(house_result['pk'], 1)
            self.assertEqual(house_result['name'], self.DATA['name'])

            self.assertEqual(house_result['latitude'], self.BASE_GPS['latitude'])
            self.assertEqual(house_result['longitude'], self.BASE_GPS['longitude'])

            house = House.objects.get(pk=house_result['pk'])
            self.assertEqual(house.pk, 1)
            self.assertEqual(house.name, self.DATA['name'])
            self.assertEqual(house.latitude, Decimal(self.BASE_GPS['latitude']))
            self.assertEqual(house.longitude, Decimal(self.BASE_GPS['longitude']))
