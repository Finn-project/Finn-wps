import json
import re
import requests
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from selenium import webdriver

from house.models import House, HouseImage
from house.serializers import HouseSerializer
from members.models import UserProfileImages
from members.serializers import UserSerializer

User = get_user_model()

# import os
#
# SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')
# if not SETTINGS_MODULE or SETTINGS_MODULE == 'config.settings':
#     SETTINGS_MODULE = 'config.settings.production'


class AirbnbCrawler:
    r = None

    def __init__(self, num_of_obj):
        self.r = requests.Session()
        self.num_of_obj = num_of_obj

        self.driver = webdriver.Chrome('/Users/smallbee/Downloads/chromedriver')
        self.driver.implicitly_wait(3)

        # url = 'https://www.airbnb.co.kr/s/homes?query=서울&section_offset=3&s_tag=ki-GoRvU&allow_override%5B%5D=&refinement_paths%5B%5D=%2Fhomes'
        # headers = {
        #     'User-agent': 'Mozilla/5.0',
        #     'cache-control': "no-cache",
        #     'accept': '*/*',
        # }
        # response = self.r.get(url, headers=headers)
        # print(response.status_code)

    def get_bootstrapdata(self):

        # city_list = ['서울특별시', '부산광역시', '대구광역시', '인천광역시',
        #              '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
        #              '경기도', '강원도', '충청북도', '충청남도', '전라북도',
        #              '전라남도', '경상북도', '경상남도', '제주특별자치도']

        city_list = ['부산광역시']

        # 페이지 횟수 계산 (최대 개수 : 18(한 페이지 숙소수) x 17(최대 페이지 수) = 306)

        # # (각 도시별) 최대 크롤링 개수 예외처리
        if self.num_of_obj > 306:
            self.num_of_obj = 306

        num_of_pages = self.num_of_obj // 18
        num_of_obj_in_the_last_page = self.num_of_obj % 18
        # # 페이지 수 계산 예외처리 (마지막 페이지(또는 첫페이지)가 18개가 아닐 경우 +1)
        if num_of_obj_in_the_last_page != 0:
            num_of_pages += 1

        for city in city_list:

            print('---------------------------------------------')
            print(f'{city} 지역의 숙소를 크롤링 시작')
            print('---------------------------------------------')

            for num in range(num_of_pages):

                url = f'https://www.airbnb.co.kr/s/homes?query={city}&section_offset={num+1}'
                headers = {
                    # 'cache-control': "no-cache",
                    'user-agent': 'Mozilla/5.0',
                    # 'postman-token': '912622a3-b1b0-49ab-89e9-ae6ab262184f',
                    # 'host': 'www.airbnb.co.kr',
                    # 'accept': '*/*',
                    # 'accept-encoding': 'gzip, deflate',
                    'cookie': '__svt=1381; cache_state=0; bev=1523934971_5ussJFyJsy%2BcIwMA; _csrf_token=V4%24.airbnb.co.kr%24G6i45M0XMrs%24reAsEi8IPWdU9YJsn2apAPDEIOtNCuY26kcvWPawU70%3D; _user_attributes=%7B%22curr%22%3A%22KRW%22%2C%22guest_exchange%22%3A1065.3037100000001%2C%22device_profiling_session_id%22%3A%221523934971--2a4ffad382218d61b920a404%22%2C%22giftcard_profiling_session_id%22%3A%221524191091--15e1aafc93002da28999da9c%22%2C%22reservation_profiling_session_id%22%3A%221524191091--5d0afa1209cc08a109f22766%22%7D; flags=268697600; dtc_exp=1; 9f2398a3e=control; b3b78300e=control; 65e98c419=control; a8f0b01c0=control; 4b522145b=treatment; dtc_exp2=42; 3b689aa21=treatment; a405338e3=treatment; mdr_browser=desktop; Cookie_3=value'
                }

                print('------------------------------------------------')
                print(f'{city} 지역의 숙소 검색결과 목록 중 "{num+1}" 페이지를 크롤링 중입니다..')
                print('------------------------------------------------')

                # response = requests.get(url)
                # response = self.r.get(url, headers=headers)
                # response = requests.get(url, headers=headers)

                # print(response.status_code)
                # html = response.text
                # if not response.status_code == 200:
                #     # requests를 통해 data 받는 것이 실패하면 해당 원인을 파악하기 위해
                #     # response 값을 출력한 뒤 종료
                #     print(html)
                #     return

                self.driver.get(url)
                html = self.driver.page_source

                with open('test.html', 'wt', encoding='utf8') as f:
                    f.write(html)

                bootstrap_data = re.search(r'data-hypernova-key="spaspabundlejs" data-hypernova-id=".*?">&lt;!--(.*?)--&gt;', html)
                # print(bootstrap_data.groups(1)[0:10])

                bootstrap_json = json.loads(bootstrap_data.group(1))
                print(bootstrap_json)
                # listing 18개가 들어있는 list
                listing_list = \
                bootstrap_json['bootstrapData']['reduxData']['exploreTab']['response']['explore_tabs'][0]['sections'][0][
                    'listings']

                for i in range(len(listing_list)):
                    print(listing_list[i]['listing'])
                    listing = listing_list[i]['listing']

                    '''
                    1) crawling data로 host_user 회원가입 또는 회원정보 가져오기
                    '''
                    host_user_data = {
                        'username': str(listing['user']['id']) + '@finn.com',
                        'password': str(listing['user']['id']) + '@finn.com',
                        'first_name': listing['user']['first_name'],
                    }
                    j = 0
                    try:
                        user = User.objects.get(username=host_user_data['username'])
                    except:
                        j = 1
                        user = User.objects.create_django_user(**host_user_data)

                    # host_user image 생성을 위한 OneToOne model 생성(or 가져오기)
                    img, _ = UserProfileImages.objects.get_or_create(user=user)
                    if j == 1:
                        # host_user가 처음 생성될 때에만 profile image를 생성한다.
                        # img.img_profile_28 = listing['user']['thumbnail_url'] if listing['user']['has_profile_pic'] is True else ''
                        # img.img_profile_225 = listing['user']['picture_url'] if listing['user']['has_profile_pic'] is True else ''
                        # img.img_profile = listing['user']['picture_url'] if listing['user']['has_profile_pic'] is True else ''
                        # img.save()

                        binary_data = requests.get(listing['user']['picture_url']).content

                        img.img_profile.save('img_prifile.png', ContentFile(binary_data))
                        img.img_profile_28.save('img_prifile_28.png', ContentFile(binary_data))
                        img.img_profile_225.save('img_prifile_225.png', ContentFile(binary_data))
                        print(f'{i+1}번째 host_user [생성 완료]')
                    else:
                        print(f'{i+1}번째 host_user [업데이트 완료]')

                    print(UserSerializer(user).data)

                    '''
                    2) crawling data로 house 객체 DB에 직접 생성하기
                    '''
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
                            # 'img_cover': listing['picture_urls'][0],
                            # -> image url 경로만 저장하는 법
                            # 'img_cover': ContentFile(requests.get(listing['picture_urls'][0]).content) if listing.get('picture_urls') else '',
                            # -> image 파일을 전달해서 생성하려고 했으나

                            'host': user,
                        }
                    house, house_created = House.objects.update_or_create(
                        name=listing['name'],
                        defaults=house_data,
                    )
                    house.img_cover.save('house_crawling_cover.png', ContentFile(requests.get(listing['picture_urls'][0]).content))

                    # 만들어진 house 객체에 ForeignKey로 연결된 HouseImage 객체 생성하기
                    # houseimage1 = HouseImage.objects.create(house=house)
                    # houseimage2 = HouseImage.objects.create(house=house)
                    # houseimage1.image = listing['picture_urls'][1] if len(listing['picture_urls']) > 1 else ''
                    # houseimage2.image = listing['picture_urls'][2] if len(listing['picture_urls']) > 2 else ''
                    # houseimage1.save()
                    # houseimage2.save()
                    response = requests.get(listing['picture_urls'][1])
                    response2 = requests.get(listing['picture_urls'][2])
                    binary_data = response.content
                    binary_data2 = response2.content

                    # house.images.create(image=ContentFile(binary_data))
                    # house.images.create(image=ContentFile(binary_data2))

                    houseimage1 = HouseImage.objects.create(house=house)
                    houseimage2 = HouseImage.objects.create(house=house)

                    houseimage1.image.save('house_crawling_inner1.png', ContentFile(binary_data))
                    houseimage2.image.save('house_crawling_inner2.png', ContentFile(binary_data2))

                    if house_created is True:
                        print(f'{i+1}번째 house [생성 완료]')
                    else:
                        print(f'{i+1}번째 house [업데이트 완료]')

                    # 커버이미지만 있고, 내부 이미지가 존재하지 않는 경우 예외처리가 필요
                    print(f"내부 이미지 존재 여부: {len(listing['picture_urls']) > 1}")
                    print(f"이미지 개수(커버포함): {len(listing['picture_urls'])}")
                    # print(f"사진 개수(커버이미지포함): {listing['picture_count']}")

                    print('크롤링 결과 데이터')
                    print('================================================')
                    print(HouseSerializer(house).data)
                    print('================================================')

                    # 마지막 페이지일 경우 num_of_obj_in_the_last_page 개수만큼만
                    # 크롤링하고 해당 도시의 크롤링 종료
                    if num + 1 == num_of_pages:
                        if i+1 == num_of_obj_in_the_last_page:
                            break

                    # if self.num_of_obj > 0:
                    #     if i+1 == self.num_of_obj:
                    #         break
