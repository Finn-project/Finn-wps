import json
import os
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# 한줄로 처리
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from members.models import UserProfileImages
from members.serializers import UserSerializer
from house.models import House, HouseImage
from house.serializers import HouseSerializer


User = get_user_model()


class AirbnbCrawler:

    def __init__(self, num_of_obj):
        self.num_of_obj = num_of_obj

        self.driver = webdriver.Chrome('/Users/smallbee/Downloads/chromedriver')
        self.driver.implicitly_wait(3)

    def house_detail_crawling(self, house_id):

        house_url = f'https://www.airbnb.co.kr/rooms/{house_id}'
        self.driver.get(house_url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        if soup.select_one('span._13nd2f7d > h1._1xu9tpch') is None:
            with open('test2.html', 'wt', encoding='utf8') as f:
                f.write(html)
            print(f'**서버 통신 이상** | {len(html)}')
            return
        else:
            print(f'-서버 통신 정상- | {len(html)}')

        # (1) Regulation + BeautifulSoup 이용한 crawling

        # 1) name
        name = soup.select_one('span._13nd2f7d > h1._1xu9tpch').get_text(strip=True)
        print(name)

        # 2) description
        span_list = soup.select_one('p._6z3til').select('span')
        description_list = []
        for index, span in enumerate(span_list):
            no_first_span = re.sub('<span>', '', str(span))
            if index + 1 != len(span_list):
                # 맨 마지막 순회에서는 \n 넣지 않도록
                no_span = re.sub('</span>', '\n', no_first_span)
            else:
                no_span = re.sub('</span>', '', no_first_span)
            description_list.append(no_span)
            if index == 3:
                break
                # '정확한 위치는 예약 완료 후에 표시됩니다'를 제외하기 위한 예외처리
        description = ''.join(description_list)
        print(description)

        # 3) 4) 5) 6) room, bed, bathroom, personnel
        span_list = soup.select('div._1thk0tsb > span._y8ard79')
        basic_info_list = []
        for span in span_list:
            text = span.get_text(strip=True)
            basic_info_list.append(text)
        # print(basic_info_list)

        def find_num(string):
            result = re.search(r'.*?(\d).*?', string)
            if result is not None:
                num = result.group(1)
            else:
                num = 1
                # 원룸일 경우 예외 처리
            return num

        room = find_num(basic_info_list[1])
        bed = find_num(basic_info_list[2])
        bathroom = find_num(basic_info_list[3])
        personnel = find_num(basic_info_list[0])
        # print(personnel)
        # print(room)
        # print(bed)
        # print(bathroom)

        # 7) price_per_night
        price_str = soup.select_one('div._12cv0xt > div > div._36rlri > span._10cqp947 > span').text
        # print(price_str)
        price_per_night = int(re.sub(',', '', re.sub('₩', '', price_str)))

        # 8) lat, lng (Selenium으로도 brower 조회 데이터를 불러오지 못해 실패)
        #                             neighborhood > div > div > div > div._e296pg > section > div._e296pg > div > div._1fmyluo4 > div > div > div > div:nth-child(9) > div:nth-child(2) > a
        #                             neighborhood > div > div > div > div._e296pg > section > div._e296pg > div > div._1fmyluo4 > div > div > div > div:nth-child(2) > a
        # href = soup.select_one('div#neighborhood > div > div > div > div._e296pg > section > div._e296pg > div > div._1fmyluo4')
        # print(href)
        # lat_lng = re.search('.*?=(.*?),(.*?)=', href)
        # lat = lat_lng.group(1)
        # lng = lat_lng.group(2)

        # (2) json 내부 데이터 parsing 활용

        bootstrap_data = re.search(r'data-hypernova-key="spaspabundlejs" data-hypernova-id=".*?">&lt;!--(.*?)--&gt;</script>', html)
        # print(bootstrap_data.group(1))
        bootstrap_json = json.loads(bootstrap_data.group(1))
        # print(bootstrap_json)
        listing_dict = \
            bootstrap_json['bootstrapData']['reduxData']['homePDP']['listingInfo']['listing']

        # # house_info

        # 1) name (BeutifulSoup crawling 데이터로 사용)
        # name = listing_dict['p3_subject']
        # print(name)

        # 8) minimum_check_in_duration = 1,
        minimum_check_in_duration = listing_dict['min_nights']
        print(minimum_check_in_duration)

        # 9) 10) 11) 12) 13)
        address_list = listing_dict['location_title'].split(', ')
        print(address_list)
        length = len(address_list)
        # 9) country
        country = address_list[length-1]
        print(country)
        # 10) city
        city = address_list[length-2]
        print(city)
        # 11) district
        district = listing_dict['localized_city']
        # district = address_list[length-3]
        print(district)
        # 12) dong = ''
        # 13) address1
        address1 = address_list[0] if length > 3 else ''
        # 주소 명칭이 4개 있을 경우 가장 첫번째 단어를 상세주소(address1)에 할당
        print(address1)

        # 14) latitude
        lat = listing_dict['lat']
        print(lat)

        # 15) longitude
        lng = listing_dict['lng']
        print(lng)

        # 16) img_cover
        img_cover_url = listing_dict['photos'][0]['large']
        print(img_cover_url)

        # 17) inner
        # inner images 존재 x 경우 예외처리(1)
        if len(listing_dict['photos']) > 1:
            inner_img_url_1 = listing_dict['photos'][1]['large']
            print(inner_img_url_1)
        else:
            inner_img_url_1 = ''

        # inner images 존재 x 경우 예외처리(2)
        if len(listing_dict['photos']) > 2:
            inner_img_url_2 = listing_dict['photos'][2]['large']
            print(inner_img_url_2)
        else:
            inner_img_url_2 = ''

        # 18)
        # disable_days = [
        #     '2014-01-01',
        #     '2014-02-01',
        #     '2014-03-01',
        #     '2014-04-01',
        # ],

        # 19) amenities = [],

        # 20) facilities = [1, 2, 3, 4, 5],

        # 21) maximum_check_in_duration = 3,
        # 22) maximum_check_in_range = 90,
        # 23) personnel
        # personnel = listing_dict['person_capacity']
        # print(personnel)

        house_data = {
            'house_id': house_id,
            # 'house_type': 'HO',
            'name': name,
            'description': description,
            'room': room,
            'bed': bed,
            'bathroom': bathroom,
            'personnel': personnel,
            # 'amenities': [],
            # 'facilities': [1, 2, 3, 4, 5],
            'minimum_check_in_duration': minimum_check_in_duration,
            'maximum_check_in_duration': 5,
            'maximum_check_in_range': 90,
            'price_per_night': price_per_night,
            'country': country,
            'city': city,
            'district': district,
            # 'dong': 'default',
            'address1': address1,
            'lat': lat,
            'lng': lng,
            # 'disable_days': [
            #     '2014-01-01',
            #     '2014-02-01',
            #     '2014-03-01',
            #     '2014-04-01',
            # ],
            'img_cover_url': img_cover_url,
            'inner_img_url_1': inner_img_url_1,
            'inner_img_url_2': inner_img_url_2,
        }

        # # host_user info

        # 1) username
        username = str(listing_dict['user']['id']) + '@finn.com'
        print(username)

        # 2) first_name
        first_name = username
        print(first_name)

        # 3) img_profile path
        img_profile_url = listing_dict['user']['profile_pic_path']
        print(img_profile_url)

        host_user_data = {
            'username': username,
            'password': username,
            'first_name': first_name,
            'img_profile_url': img_profile_url,
        }
        self.create_host_user_and_house(**house_data, **host_user_data)

    def house_page_crawling(self):

        # selenium setting
        # driver = webdriver.Chrome('chromedriver')

        # 페이지 횟수 계산 (최대 개수 : 18(한 페이지 숙소수) x 17(최대 페이지 수) = 306)
        # # (각 도시별) 최대 크롤링 개수 예외처리
        if self.num_of_obj > 306:
            self.num_of_obj = 306

        num_of_pages = self.num_of_obj // 18
        num_of_obj_in_the_last_page = self.num_of_obj % 18
        # # 페이지 수 계산 예외처리 (마지막 페이지(또는 첫페이지)가 18개가 아닐 경우 +1)
        if num_of_obj_in_the_last_page != 0:
            num_of_pages += 1

        # city_list = ['서울특별시', '부산광역시', '대구광역시', '인천광역시',
        #              '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
        #              '경기도', '강원도', '충청북도', '충청남도', '전라북도',
        #              '전라남도', '경상북도', '경상남도', '제주특별자치도']
        city_list = ['서울특별시']

        for city in city_list:

            print('---------------------------------------------------------------')
            print(f'{city} 지역의 숙소를 크롤링 시작')
            print('---------------------------------------------------------------')

            for num in range(num_of_pages):

                print('---------------------------------------------------------------')
                print(f'{city} 지역의 숙소 검색결과 목록 중 "{num+1}" 페이지를 크롤링 중입니다..')
                print('---------------------------------------------------------------')

                url = f'https://www.airbnb.co.kr/s/homes?query={city}&section_offset={num+1}'

                self.driver.get(url)
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'lxml')

                # with open('test1.html', 'wt', encoding='utf8') as f:
                #     f.write(html)

                house_info = {}
                itemListElement_list = soup.find('div', class_='_fhph4u').find_all('div', class_='_gig1e7')
                house_num = len(itemListElement_list)
                for i in itemListElement_list:
                    house_id_str = i.select_one('div > div > div').get('id')
                    house_id = house_id_str.split('-')[1]

                    print(f'숙소 {house_id}를 크롤링합니다.')
                    self.house_detail_crawling(house_id)
                    break

    def create_host_user_and_house(self, **kwargs):
        host_user_data = {
            'username': kwargs['username'],
            'password': kwargs['password'],
            'first_name': kwargs['first_name'],
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
            binary_data = requests.get(kwargs['img_profile_url']).content
            img.img_profile.save('img_prifile.png', ContentFile(binary_data))
            img.img_profile_28.save('img_prifile_28.png', ContentFile(binary_data))
            img.img_profile_225.save('img_prifile_225.png', ContentFile(binary_data))
            print(f'host_user({kwargs["username"]}) [생성 완료]')
        else:
            print(f'host_user({kwargs["username"]}) [업데이트 완료]')

        print('크롤링 결과 데이터')
        print('================================================')
        print(UserSerializer(user).data)
        print('================================================')

        house_data = {
            # 'house_type': 'HO',
            'name': kwargs['name'],
            'description': kwargs['description'],
            'room': kwargs['room'],
            'bed': kwargs['bed'],
            'bathroom': kwargs['bathroom'],
            'personnel': kwargs['personnel'],
            # 'amenities': [],
            # 'facilities': [1, 2, 3, 4, 5],
            'minimum_check_in_duration': kwargs['minimum_check_in_duration'],
            'maximum_check_in_duration': 5,
            'maximum_check_in_range': 90,
            'price_per_night': kwargs['price_per_night'],
            'country': kwargs['country'],
            'city': kwargs['city'],
            'district': kwargs['district'],
            # 'dong': 'default',
            'address1': kwargs['address1'],
            'latitude': kwargs['lat'],
            'longitude': kwargs['lng'],
            # 'disable_days': [
            #     '2014-01-01',
            #     '2014-02-01',
            #     '2014-03-01',
            #     '2014-04-01',
            # ],

            'host': user,
        }

        # img_cover 저장 (cover)
        house, house_created = House.objects.update_or_create(
            name=kwargs['name'],
            defaults=house_data,
        )
        house.img_cover.save('house_crawling_cover.png', ContentFile(requests.get(kwargs['img_cover_url']).content))

        # house_images 저장 (inner)
        if kwargs.get('inner_img_url_1'):
            binary_data1 = requests.get(kwargs['inner_img_url_1']).content
            house_image_1 = HouseImage.objects.create(house=house)
            house_image_1.image.save('house_crawling_inner1.png', ContentFile(binary_data1))
        if kwargs.get('inner_img_url_2'):
            binary_data2 = requests.get(kwargs['inner_img_url_2']).content
            house_image_2 = HouseImage.objects.create(house=house)
            house_image_2.image.save('house_crawling_inner2.png', ContentFile(binary_data2))

        if house_created is True:
            print(f"house({kwargs['house_id']}) [생성 완료]")
        else:
            print(f"house({kwargs['house_id']}) [업데이트 완료]")

        print('크롤링 결과 데이터')
        print('================================================')
        print(HouseSerializer(house).data)
        print('================================================')


if __name__ == '__main__':
    air = AirbnbCrawler(3)
    # air.house_page_crawling()
    # air.house_detail_crawling(17563112)
    air.house_detail_crawling(19350356)
