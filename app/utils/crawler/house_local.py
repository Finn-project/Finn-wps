# import os
#
# SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')
# if not SETTINGS_MODULE or SETTINGS_MODULE == 'config.settings':
#     SETTINGS_MODULE = 'config.settings.local'

import json
import re
import requests

# from rest_framework.authtoken.models import Token
# from house.models import House
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile


class AirbnbCrawler:
    r = None

    def __init__(self):
        self.r = requests.Session()

        # url = 'https://www.airbnb.co.kr/s/homes?query=서울&section_offset=3&s_tag=ki-GoRvU&allow_override%5B%5D=&refinement_paths%5B%5D=%2Fhomes'
        # headers = {
        #     'User-agent': 'Mozilla/5.0',
        #     'cache-control': "no-cache",
        #     'accept': '*/*',
        # }
        # response = self.r.get(url, headers=headers)
        # print(response.status_code)

    def get_bootstrapdata(self):
        url = 'https://www.airbnb.co.kr/s/homes?query=서울특별시&section_offset=5'
        headers = {
            # 'cache-control': "no-cache",
            # 'user-agent': 'Mozilla/5.0',
            # 'postman-token': '912622a3-b1b0-49ab-89e9-ae6ab262184f',
            # 'host': 'www.airbnb.co.kr',
            # 'accept': '*/*',
            # 'accept-encoding': 'gzip, deflate',
            # 'cookie': '__svt=1381; cache_state=0; bev=1523934971_5ussJFyJsy%2BcIwMA; _csrf_token=V4%24.airbnb.co.kr%24G6i45M0XMrs%24reAsEi8IPWdU9YJsn2apAPDEIOtNCuY26kcvWPawU70%3D; jitney_client_session_id=2f0abc70-0be3-4f8d-aac3-84363faa4a73; jitney_client_session_created_at=1523957423; jitney_client_session_updated_at=1523957423; _user_attributes=%7B%22curr%22%3A%22KRW%22%2C%22guest_exchange%22%3A1072.3055650000001%2C%22device_profiling_session_id%22%3A%221523934971--2a4ffad382218d61b920a404%22%2C%22giftcard_profiling_session_id%22%3A%221523957424--c718f2fe50a984671b19354d%22%2C%22reservation_profiling_session_id%22%3A%221523957424--48f5ec024f0477b119d21220%22%7D; flags=268697600; dtc_exp=1; 9f2398a3e=control; b3b78300e=control; 65e98c419=control; a8f0b01c0=control; 4b522145b=treatment',
            'cookie': '__svt=1381; cache_state=0; bev=1523934971_5ussJFyJsy%2BcIwMA; _csrf_token=V4%24.airbnb.co.kr%24G6i45M0XMrs%24reAsEi8IPWdU9YJsn2apAPDEIOtNCuY26kcvWPawU70%3D; jitney_client_session_id=7409e864-df24-46e1-9331-5793fc836ac4; jitney_client_session_created_at=1523979136; jitney_client_session_updated_at=1523979136; _user_attributes=%7B%22curr%22%3A%22KRW%22%2C%22guest_exchange%22%3A1072.3055650000001%2C%22device_profiling_session_id%22%3A%221523934971--2a4ffad382218d61b920a404%22%2C%22giftcard_profiling_session_id%22%3A%221523979138--ded77b2c438cd5e5b8f64f9e%22%2C%22reservation_profiling_session_id%22%3A%221523979138--403d68f09bc045f3db938d8a%22%7D; flags=268697600; dtc_exp=1; 9f2398a3e=control; b3b78300e=control; 65e98c419=control; a8f0b01c0=control; 4b522145b=treatment; Cookie_1=value; mdr_browser=desktop',
        }

        # 1) Airbnb web crawling
        # response = requests.get(url)
        # response = self.r.get(url, headers=headers)

        # response = requests.get(url, headers=headers)
        # print(response.status_code)
        # source = response.text

        # 2) local airbnb_data.html
        source = open('airbnb_data.html', 'rt', encoding='utf8').read()
        print(source)

        bootstrap_data = re.search(r'data-hypernova-key="spaspabundlejs" data-hypernova-id=".*?"><!--(.*?)--></script>', source)
        # print(bootstrap_data.groups(1)[0:10])
        bootstrap_json = json.loads(bootstrap_data.group(1))

        # listing 18개가 들어있는 list
        listing_list = \
        bootstrap_json['bootstrapData']['reduxData']['exploreTab']['response']['explore_tabs'][0]['sections'][0][
            'listings']

        for i in range(len(listing_list)):
            print(listing_list[i]['listing'])
            listing = listing_list[i]['listing']

            # crawling data에서 image 다운받기
            # img_cover_binary_data = requests.get(listing['picture_url']).content

            response = requests.get(listing['picture_urls'][0]).content
            print(type(response))

            print(response)
            print(ContentFile(response))
            print(type(ContentFile(response)))
            # print(ContentFile(requests.get(listing['picture_urls'][2]).content))

            temp_file = NamedTemporaryFile(suffix='.png')
            temp_file.seek(0)
            temp_file.write(response)
            temp_file.seek(0)
            print(temp_file.name)
            img_cover = open(temp_file.name, 'rb')
            print(img_cover)
            print(type(img_cover))

            # crawling data 로 house info 채우기
            data = {
                'house_type': 'HO',
                'name': listing['name'],
                'description': '테스트용 집입니다.',
                'room': listing['bedrooms'],
                'bed': listing['beds'],
                'bathroom': listing['bathrooms'],
                'personnel': listing['person_capacity'],
                'amenities': [],
                'facilities': [1, 2, 3, 4, 5],
                'minimum_check_in_duration': 1,
                'maximum_check_in_duration': 3,
                'maximum_check_in_range': 90,
                'price_per_night': 100000,
                'country': 'default',
                'city': 'default',
                'district': listing['localized_city'],
                'dong': 'default',
                'address1': 'default',
                # 'address2': '희망빌라 2동 301호',
                'latitude': listing['lat'],
                'longitude': listing['lng'],
                'disable_days': [
                    '2014-01-01',
                    '2014-02-01',
                    '2014-03-01',
                    '2014-04-01',
                ],
                # 'img_cover': ContentFile(requests.get(listing['picture_urls'][0]).content),
                'img_cover': img_cover,
                # 'house_images': [
                #     ContentFile(requests.get(listing['picture_urls'][1]).content),
                #     ContentFile(requests.get(listing['picture_urls'][2]).content),
                # ],
            }

            # host_user의 Token 값 header에 넣기

            # 회원가입

            # 로그인
            user_data = {
                'username': 'iostest@gmail.com',
                'password': 'iostestpw'
            }
            # response = requests.post('/user/login/', user_data)
            response = requests.post('http://localhost:8000/user/login/', user_data)
            result = json.loads(response.text)
            token = result['token']

            headers = {
                'Authorization': 'Token ' + token,
            }

            # response = requests.post('/house/', data, headers=headers)
            response = requests.post('http://localhost:8000/house/', data, headers=headers)
            print(response)
            print(i+1)

            img_cover.close()
            temp_file.close()


airbnb = AirbnbCrawler()
airbnb.get_bootstrapdata()
