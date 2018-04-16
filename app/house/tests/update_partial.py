import datetime
import os
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from utils.image.file import upload_file_cmp
from utils.image.resize import clear_imagekit_test_files
from ..models import Amenities, Facilities, House, HouseDisableDay, HouseImage

__all__ = (
    'HousePartialUpdateTest',
)

User = get_user_model()


class HousePartialUpdateTest(APITestCase):
    URL = '/house/'
    HOUSE_PK = 1

    AMENITIES_LIST = ['TV', '에어컨', '전자렌지', '커피포트', '컴퓨터', '공기청정기']
    FACILITIES_LIST = ['수영장', '엘리베이터', '세탁소', '노래방', '오락실', '온천']

    BASE_DISABLE_DAYS = [
        '2014-01-01',
        '2014-02-01',
        '2014-03-01',
        '2014-04-01',
    ]

    BASE_AMENITIES = [1, 2, 3, 4]
    BASE_FACILITIES = [1, 2, 3]

    BASE_DATA = {
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
        'latitude': '12.1234567',
        'longitude': '123.1234567',
    }

    UPDATE_DATA = {
        'house_type': House.HOUSE_TYPE_APARTMENT,
        'address1': '777-1',
        # 'address2': '희망빌라 2동 301호',
        'latitude': '12.1234567',
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

        self.BASE_DATA['host'] = self.user
        house = House.objects.create(**self.BASE_DATA)

        file_path = os.path.join(settings.STATIC_DIR, 'iu.jpg')
        house_image1_path = os.path.join(settings.STATIC_DIR, 'test', 'test_inner_image.jpg')
        house_image2_path = os.path.join(settings.STATIC_DIR, 'test', 'test_outer_image.jpg')

        img_cover = open(file_path, 'rb')
        house_image1 = open(house_image1_path, 'rb')
        house_image2 = open(house_image2_path, 'rb')

        house.img_cover.save('iu.jpg', img_cover)
        houseimage1 = HouseImage.objects.create(house=house)
        houseimage2 = HouseImage.objects.create(house=house)
        houseimage1.image.save('test_inner_image.jpg', house_image1)
        houseimage2.image.save('test_outer_image.jpg', house_image2)

        img_cover.close()
        house_image1.close()
        house_image2.close()

        self.user.is_host = True
        self.user.save()

        for amenity in self.BASE_AMENITIES:
            house.amenities.add(amenity)

        for facility in self.BASE_FACILITIES:
            house.facilities.add(facility)

        for disable_day in self.BASE_DISABLE_DAYS:
            date_instance, created = HouseDisableDay.objects.get_or_create(date=disable_day)
            house.disable_days.add(date_instance)

        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key,
        )
        self.assertTrue(upload_file_cmp(file_path=house_image1_path, img_name=house.images.first().image.name))
        self.assertTrue(upload_file_cmp(file_path=house_image2_path, img_name=house.images.last().image.name))

    def test_partial_update_house(self):
        file_path = os.path.join(settings.STATIC_DIR, 'img_profile_default.png')
        house_image1_path = os.path.join(settings.STATIC_DIR, 'iu.jpg')
        img_cover = open(file_path, 'rb')
        house_image1 = open(house_image1_path, 'rb')

        self.UPDATE_DATA['img_cover'] = img_cover
        self.UPDATE_DATA['house_images'] = [house_image1, ]

        response = self.client.patch(self.URL + f'{self.HOUSE_PK}/', self.UPDATE_DATA)

        img_cover.close()
        house_image1.close()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['house_type'], self.UPDATE_DATA['house_type'])
        self.assertEqual(response.data['name'], self.BASE_DATA['name'])
        self.assertEqual(response.data['description'], self.BASE_DATA['description'])
        self.assertEqual(response.data['room'], self.BASE_DATA['room'])
        self.assertEqual(response.data['bed'], self.BASE_DATA['bed'])
        self.assertEqual(response.data['bathroom'], self.BASE_DATA['bathroom'])
        self.assertEqual(response.data['personnel'], self.BASE_DATA['personnel'])
        self.assertEqual(response.data['amenities'], self.BASE_AMENITIES)
        self.assertEqual(response.data['facilities'], self.BASE_FACILITIES)
        self.assertEqual(response.data['minimum_check_in_duration'], self.BASE_DATA['minimum_check_in_duration'])
        self.assertEqual(response.data['maximum_check_in_duration'], self.BASE_DATA['maximum_check_in_duration'])
        self.assertEqual(response.data['maximum_check_in_range'], self.BASE_DATA['maximum_check_in_range'])
        self.assertEqual(response.data['price_per_night'], self.BASE_DATA['price_per_night'])
        self.assertEqual(response.data['created_date'], datetime.date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['modified_date'], datetime.date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['host']['pk'], self.user.pk)
        self.assertEqual(response.data['country'], self.BASE_DATA['country'])
        self.assertEqual(response.data['city'], self.BASE_DATA['city'])
        self.assertEqual(response.data['district'], self.BASE_DATA['district'])
        self.assertEqual(response.data['dong'], self.BASE_DATA['dong'])
        self.assertEqual(response.data['address1'], self.UPDATE_DATA['address1'])
        # self.assertEqual(response.data['address2'], self.UPDATE_DATA['address2'])
        self.assertEqual(response.data['latitude'], self.UPDATE_DATA['latitude'])
        self.assertEqual(response.data['longitude'], self.BASE_DATA['longitude'])

        self.assertIsNotNone(response.data['disable_days'], 'disable_days')
        for index, date in enumerate(response.data['disable_days']):
            self.assertEqual(date.strftime('%Y-%m-%d'), self.BASE_DISABLE_DAYS[index])

        house = House.objects.get(pk=response.data['pk'])
        self.assertEqual(house.house_type, self.UPDATE_DATA['house_type'])
        self.assertEqual(house.name, self.BASE_DATA['name'])
        self.assertEqual(house.description, self.BASE_DATA['description'])
        self.assertEqual(house.room, self.BASE_DATA['room'])
        self.assertEqual(house.bed, self.BASE_DATA['bed'])
        self.assertEqual(house.bathroom, self.BASE_DATA['bathroom'])
        self.assertEqual(house.personnel, self.BASE_DATA['personnel'])
        self.assertEqual(list(house.amenities.values_list('pk', flat=True)), self.BASE_AMENITIES)
        self.assertEqual(list(house.facilities.values_list('pk', flat=True)), self.BASE_FACILITIES)
        self.assertEqual(house.minimum_check_in_duration, self.BASE_DATA['minimum_check_in_duration'])
        self.assertEqual(house.maximum_check_in_duration, self.BASE_DATA['maximum_check_in_duration'])
        self.assertEqual(house.maximum_check_in_range, self.BASE_DATA['maximum_check_in_range'])
        self.assertEqual(house.price_per_night, self.BASE_DATA['price_per_night'])
        self.assertEqual(house.created_date, datetime.date.today())
        self.assertEqual(house.modified_date, datetime.date.today())
        self.assertEqual(house.host.pk, self.user.pk)
        self.assertEqual(house.host.is_host, True)
        self.assertEqual(house.country, self.BASE_DATA['country'])
        self.assertEqual(house.city, self.BASE_DATA['city'])
        self.assertEqual(house.district, self.BASE_DATA['district'])
        self.assertEqual(house.dong, self.BASE_DATA['dong'])
        self.assertEqual(house.address1, self.UPDATE_DATA['address1'])
        # self.assertEqual(house.address2, self.UPDATE_DATA['address2'])
        self.assertEqual(house.latitude, Decimal(self.UPDATE_DATA['latitude']))
        self.assertEqual(house.longitude, Decimal(self.BASE_DATA['longitude']))

        self.assertEqual(house.disable_days.count(), len(self.BASE_DISABLE_DAYS))
        disable_day_list = list(house.disable_days.values_list('date', flat=True))
        for index, date in enumerate(disable_day_list):
            self.assertEqual(date.strftime('%Y-%m-%d'), self.BASE_DISABLE_DAYS[index])

        self.assertTrue(upload_file_cmp(file_path=file_path, img_name=house.img_cover.name))
        self.assertTrue(upload_file_cmp(file_path=house_image1_path, img_name=house.images.first().image.name))

        clear_imagekit_test_files()
