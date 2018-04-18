# import os
#
# SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')
# if not SETTINGS_MODULE or SETTINGS_MODULE == 'config.settings':
#     SETTINGS_MODULE = 'config.settings.local'

import json
import re
import requests
from django.contrib.auth import get_user_model
from house.models import House, HouseImage
from house.serializers import HouseSerializer

User = get_user_model()


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
        url = 'https://www.airbnb.co.kr/s/homes?query=서울특별시&section_offset=3'
        headers = {
            # 'cache-control': "no-cache",
            'user-agent': 'Mozilla/5.0',
            # 'postman-token': '912622a3-b1b0-49ab-89e9-ae6ab262184f',
            # 'host': 'www.airbnb.co.kr',
            # 'accept': '*/*',
            # 'accept-encoding': 'gzip, deflate',
            # 'cookie': '__svt=1381; cache_state=0; bev=1523934971_5ussJFyJsy%2BcIwMA; _csrf_token=V4%24.airbnb.co.kr%24G6i45M0XMrs%24reAsEi8IPWdU9YJsn2apAPDEIOtNCuY26kcvWPawU70%3D; jitney_client_session_id=2f0abc70-0be3-4f8d-aac3-84363faa4a73; jitney_client_session_created_at=1523957423; jitney_client_session_updated_at=1523957423; _user_attributes=%7B%22curr%22%3A%22KRW%22%2C%22guest_exchange%22%3A1072.3055650000001%2C%22device_profiling_session_id%22%3A%221523934971--2a4ffad382218d61b920a404%22%2C%22giftcard_profiling_session_id%22%3A%221523957424--c718f2fe50a984671b19354d%22%2C%22reservation_profiling_session_id%22%3A%221523957424--48f5ec024f0477b119d21220%22%7D; flags=268697600; dtc_exp=1; 9f2398a3e=control; b3b78300e=control; 65e98c419=control; a8f0b01c0=control; 4b522145b=treatment',
            'cookie': '__svt=1381; cache_state=0; bev=1523934971_5ussJFyJsy%2BcIwMA; _csrf_token=V4%24.airbnb.co.kr%24G6i45M0XMrs%24reAsEi8IPWdU9YJsn2apAPDEIOtNCuY26kcvWPawU70%3D; jitney_client_session_id=7409e864-df24-46e1-9331-5793fc836ac4; jitney_client_session_created_at=1523979136; jitney_client_session_updated_at=1523981422; _user_attributes=%7B%22curr%22%3A%22KRW%22%2C%22guest_exchange%22%3A1072.3055650000001%2C%22device_profiling_session_id%22%3A%221523934971--2a4ffad382218d61b920a404%22%2C%22giftcard_profiling_session_id%22%3A%221523979138--ded77b2c438cd5e5b8f64f9e%22%2C%22reservation_profiling_session_id%22%3A%221523979138--403d68f09bc045f3db938d8a%22%7D; flags=268697600; dtc_exp=1; 9f2398a3e=control; b3b78300e=control; 65e98c419=control; a8f0b01c0=control; 4b522145b=treatment; Cookie_1=value',
        }

        # response = requests.get(url)
        # response = self.r.get(url, headers=headers)
        response = requests.get(url, headers=headers)

        print(response.status_code)
        source = response.text
        if not response.status_code == 200:
            # requests를 통해 data 받는 것이 실패하면 해당 원인을 파악하기 위해
            # response 값을 출력한 뒤 종료
            print(source)
            return

        bootstrap_data = re.search(r'data-hypernova-key="spaspabundlejs" data-hypernova-id=".*?"><!--(.*?)--></script>', source)
        # print(bootstrap_data.groups(1)[0:10])
        bootstrap_json = json.loads(bootstrap_data.group(1))

        # listing 18개가 들어있는 list
        listing_list = \
        bootstrap_json['bootstrapData']['reduxData']['exploreTab']['response']['explore_tabs'][0]['sections'][0][
            'listings']

        for i in range(len(listing_list)):
            # print(listing_list[i]['listing'])
            listing = listing_list[i]['listing']

            # crawling data에서 image 다운받아서 직접 저장소에 넣으려고
            # 아래 과정을 진행했으나, 이미지 url만 저장하는 방법을 사용함.
            # response = requests.get(listing['picture_urls'][0]).content
            # temp_file = NamedTemporaryFile(suffix='.png')
            # temp_file.seek(0)
            # temp_file.write(response)
            # temp_file.seek(0)
            # img_cover = open(temp_file.name, 'rb')
            # print(type(img_cover))

            # 커버이미지만 있고, 내부 이미지가 존재하지 않는 경우 예외처리가 필요
            print(f"내부 이미지 존재 여부: {len(listing['picture_urls']) > 1}")
            print(f"이미지 개수(커버포함): {len(listing['picture_urls'])}")
            # print(f"사진 개수(커버이미지포함): {listing['picture_count']}")

            # crawling data로 host_user 회원가입 또는 회원정보 가져오기
            host_user_data = {
                'username': str(listing['user']['id']) + '@gmail.com',
                'password': str(listing['user']['id']) + '@gmail.com',
                'first_name': listing['user']['first_name'],
            }
            try:
                user = User.objects.get(username=host_user_data['username'])
            except:
                user = User.objects.create_django_user(**host_user_data)

            # crawling data로 house 객체 DB에 직접 생성하기
            house_data = {
                    # 'house_type': 'HO',
                    'name': listing['name'],
                    # 'description': 'crawling한 집입니다.',
                    'room': listing['bedrooms'],
                    'bed': listing['beds'],
                    'bathroom': listing['bathrooms'],
                    'personnel': listing['person_capacity'],
                    # 'amenities': [],
                    # 'facilities': [1, 2, 3, 4, 5],
                    'minimum_check_in_duration': 1,
                    'maximum_check_in_duration': 3,
                    'maximum_check_in_range': 90,
                    'price_per_night': 100000,
                    # 'country': 'default',
                    # 'city': 'default',
                    'district': listing['localized_city'],
                    # 'dong': 'default',
                    # 'address1': 'default',
                    'latitude': listing['lat'],
                    'longitude': listing['lng'],
                    # 'disable_days': [
                    #     '2014-01-01',
                    #     '2014-02-01',
                    #     '2014-03-01',
                    #     '2014-04-01',
                    # ],
                    'img_cover': listing['picture_urls'][0],
                    # 'house_images': [
                    #     listing['picture_urls'][1] if len(listing['picture_urls']) > 1 else '',
                    #     listing['picture_urls'][2] if len(listing['picture_urls']) > 2 else '',
                    # ],

                    'host': user,
                }
            house, _ = House.objects.update_or_create(
                name=listing['name'],
                defaults=house_data,
            )

            # 만들어진 house 객체에 ForeignKey로 연결된 HouseImage 객체 생성하기
            houseimage1 = HouseImage.objects.create(house=house)
            houseimage2 = HouseImage.objects.create(house=house)
            houseimage1.image = listing['picture_urls'][1] if len(listing['picture_urls']) > 1 else ''
            houseimage2.image = listing['picture_urls'][2] if len(listing['picture_urls']) > 2 else ''
            houseimage1.save()
            houseimage2.save()

            print(houseimage1.image.url)
            print(houseimage2.image.url)

            print(f'{i+1}번째 house 생성 완료')
            # print(HouseSerializer(house))
            print(HouseSerializer(house).data)

            if i == 2:
                break
