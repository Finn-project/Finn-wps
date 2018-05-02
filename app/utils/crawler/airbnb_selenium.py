import json
import os
import random
import re

import datetime
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver

# 한줄로 처리
from selenium.common.exceptions import NoSuchWindowException

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from members.models import UserProfileImages
from members.serializers import UserSerializer
from house.models import House, HouseImage, HouseDisableDay
from house.serializers import HouseSerializer
from django.utils import timezone


User = get_user_model()


class AirbnbCrawler:

    def __init__(self, num_of_obj):
        self.num_of_obj = num_of_obj

        # sumin
        # self.driver = webdriver.Chrome('/home/sumin/Downloads/chromedriver')

        # vi ~/.zshrc에 하단 내용 추가해서 상대경로로 불러올 수 있도록 수정
        # export PATH=${PATH}:~/Project/Downloads
        self.driver = webdriver.Chrome('chromedriver')

        self.driver.implicitly_wait(3)

    def house_detail_crawling(self, house_id):

        house_url = f'https://www.airbnb.co.kr/rooms/{house_id}'
        self.driver.get(house_url)
        time.sleep(1)
        # self.driver.implicitly_wait(5)
        html = self.driver.page_source
        self.driver.implicitly_wait(5)
        soup = BeautifulSoup(html, 'lxml')

        # (1) Regulation + BeautifulSoup 이용한 crawling

        try:
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
            # print(description)

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
            # print(minimum_check_in_duration)

            # 9) 10) 11) 12) 13)
            address_list = listing_dict['location_title'].split(', ')
            # print(address_list)
            length = len(address_list)

            # 9) country
            country = address_list[length-1]
            # print(country)

            # 10) city
            city = address_list[length-2]
            # print(city)

            # 11) district
            district = listing_dict['localized_city']
            # district = address_list[length-3]
            # print(district)

            # 12) dong = ''

            # 13) address1
            address1 = address_list[0] if length > 3 else ''
            # 주소 명칭이 4개 있을 경우 가장 첫번째 단어를 상세주소(address1)에 할당
            # print(address1)

            # 14) latitude
            lat = listing_dict['lat']
            # print(lat)

            # 15) longitude
            lng = listing_dict['lng']
            # print(lng)

            # 16) img_cover
            img_cover_url = listing_dict['photos'][0]['large']
            # print(img_cover_url)

            # 17) inner
            # inner images 존재 x 경우 예외처리(1)
            if len(listing_dict['photos']) > 1:
                inner_img_url_1 = listing_dict['photos'][1]['large']
                # print(inner_img_url_1)
            else:
                inner_img_url_1 = ''

            # inner images 존재 x 경우 예외처리(2)
            if len(listing_dict['photos']) > 2:
                inner_img_url_2 = listing_dict['photos'][2]['large']
                # print(inner_img_url_2)
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
            # print(username)

            # 2) first_name
            first_name = listing_dict['user']['host_name']
            # print(first_name)

            # 3) img_profile path
            img_profile_url = listing_dict['user']['profile_pic_path']
            # print(img_profile_url)

            host_user_data = {
                'username': username,
                'password': username,
                'first_name': first_name,
                'img_profile_url': img_profile_url,
            }
            self.create_host_user_and_house(**house_data, **host_user_data)
        except (AttributeError, NoSuchWindowException) as e:
            print(f'#################################')
            with open('house_detail_server_log.html', 'wt', encoding='utf8') as f:
                f.write(html)
            print(f'* 서버 통신 이상 * | {len(html)}')
            print(f'exception: {e}')
            print(f'house_detail_sever_log.html 기록')
            print(f'#################################')
            pass

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

        city_list = ['서울특별시', '부산광역시', '대구광역시', '인천광역시',
                     '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
                     '경기도', '강원도', '충청북도', '충청남도', '전라북도',
                     '전라남도', '경상북도', '경상남도', '제주특별자치도']

        print('')
        print(f'다음 지역의 숙소들을 크롤링 합니다.')
        print(f'{[city for city in city_list]}')

        for city in city_list:
            print('')
            print(f'[1단계] {city} 지역의 숙소 {self.num_of_obj}개 크롤링 시작')
            print('--------------------------------------------------------------------')

            count = 0
            for num in range(num_of_pages):
                print('')
                print(f'[2단계] {city} 지역의 숙소목록 중 "{num+1}" 페이지를 크롤링 중..')
                print('--------------------------------------------------------------------')

                url = f'https://www.airbnb.co.kr/s/homes?query={city}&section_offset={num+1}'

                self.driver.get(url)
                # self.driver.implicitly_wait(5)
                time.sleep(1)
                html = self.driver.page_source
                self.driver.implicitly_wait(5)
                soup = BeautifulSoup(html, 'lxml')

                try:
                    itemListElement_list = soup.find('div', class_='_fhph4u').find_all('div', class_='_gig1e7')
                    house_num = len(itemListElement_list)
                    print(f'( 현재 페이지 하우스 개수: {house_num} )')
                    for i, item in enumerate(itemListElement_list):
                        house_id_str = item.select_one('div > div > div').get('id')
                        house_id = house_id_str.split('-')[1]
                        print('\n')
                        print(f'[3단계] 숙소({house_id}) 크롤링 시작 [{count}/{self.num_of_obj}]')
                        print('--------------------------------------------------------------------')

                        self.house_detail_crawling(house_id)
                        count += 1

                        # 현재 페이지가 크롤링 해야하는 마지막 페이지이고,
                        if num + 1 == num_of_pages:
                            # 방금 크롤링한 숙소가 크롤링 해야하는 마지막 숙소이면,
                            if i + 1 == num_of_obj_in_the_last_page:
                                # "for i in itemListElement_list" 반복문 탈출
                                # (* for num in range(num_of_pages)는 자동 종료된다.)
                                break
                except (AttributeError, NoSuchWindowException) as e:
                    print(f'#################################')
                    with open('house_page_server_log.html', 'wt', encoding='utf8') as f:
                        f.write(html)
                    print(f'* 서버 통신 이상 * | {len(html)}')
                    print(f'exception: {e}')
                    print(f'house_page_server_log.html 기록')
                    print(f'#################################')
                    continue

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
            user.is_host = True
            user.save()

        # host_user image 생성을 위한 OneToOne model 생성(or 가져오기)
        img, _ = UserProfileImages.objects.get_or_create(user=user)

        print('')
        print(f'[ host_user 크롤링 결과 데이터 ]')
        if j == 1:
            # host_user가 처음 생성될 때에만 profile image를 생성한다.
            binary_data = requests.get(kwargs['img_profile_url']).content
            img.img_profile.save('img_prifile.png', ContentFile(binary_data))
            img.img_profile_28.save('img_prifile_28.png', ContentFile(binary_data))
            img.img_profile_225.save('img_prifile_225.png', ContentFile(binary_data))
            print(f'host_user({kwargs["username"]}) 생성 완료')
        else:
            print(f'host_user({kwargs["username"]}) 업데이트 완료')
        print(UserSerializer(user).data)
        print('====================================================================')

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

        def make_random_choice_list(list_data):
            random_num = random.randint(1, len(list_data))
            # print(f'random_num: {random_num}')

            random_choice_list = []
            for i in range(random_num):
                random_choice = random.choice(list_data)
                random_choice_list.append(random_choice)
                list_data.remove(random_choice)
                # print(f'{random_choice}| {len(list_data)}개 남음')
                # print(list_data)
            # print(random_choice_list)
            return random_choice_list

        # amenities 저장
        amenities_list = [1, 2, 3, 4, 5, 6]
        random_choice_list = make_random_choice_list(amenities_list)
        house.amenities.set(random_choice_list)

        # facilities 저장
        facilities_list = [1, 2, 3, 4, 5, 6]
        random_choice_list = make_random_choice_list(facilities_list)
        house.facilities.set(random_choice_list)

        # disable_day 저장
        # (기존 house에 등록된 disable_day가 10일 미만일 때만 난수값을 생성해서 넣어준다.)
        if house.disable_days.all().count() < 10:
            now = timezone.now()
            date_now = datetime.date(now.year, now.month, now.day)

            disable_days_random_list = []
            random_num_for_disable_days = random.randint(1, 10)

            for i in range(random_num_for_disable_days):
                n = random.randint(1, 90)
                result = date_now + datetime.timedelta(n)
                disable_days_random_list.append(date_now + datetime.timedelta(n))

            # 1) set() 하면 중복만 제거
            # 2) sort() 하면 순서만 정렬
            # -> 여기서 sort()는 하나마나 의미가 없음.
            #    1. 열심히 sort()해서 날짜순으로 만들어봤자. get_or_create할 때
            #       기존에 있는 date를 그냥 가져오기때문에 어차피 날짜는 꼬임
            #    2. 실질적으로 front에게 전달되는 HouseSerializer(house).data에서
            #       실제로 json형태로 보여지는 출력값은
            #       house.disable_days.add(date_instance)를 하는 순서가 어떻든 간에
            #       pk순(더 정확하게는 created_date로 되어있음)으로 되어있어서 무조건 그것을 따른다.
            #       (예를들면 amenities와 facilities는 위에서 넣는 순서가 제멋대로인데
            #        실제 출력되는 json 값은 항상 sort()가 되어있는 것 처럼 보인다.
            #        amenities와 facilities는 db구성시 최초 생성될 때 순서대로 생성되었기 때문)

            # print(disable_days_random_list)
            disable_days_random_list = list(set(disable_days_random_list))
            # disable_days_random_list.sort()
            # 의미없어서 .sort() 주석처리
            # print(disable_days_random_list)

            for date in disable_days_random_list:
                # print(date)
                date_instance, _ = HouseDisableDay.objects.get_or_create(date=str(date))
                house.disable_days.add(date_instance)

        print('')
        print(f'[ house 크롤링 결과 데이터 ]')
        if house_created is True:
            print(f"house({kwargs['house_id']}) 생성 완료")
        else:
            print(f"house({kwargs['house_id']}) 업데이트 완료")
        print(HouseSerializer(house).data)
print('====================================================================')


if __name__ == '__main__':
    air = AirbnbCrawler(18)
    # air.house_page_crawling()
    # air.house_detail_crawling(17563112)
    # air.house_detail_crawling(19350356)
    # air.house_detail_crawling(23810665)
    # air.house_detail_crawling(15977440)
    air.house_detail_crawling(15512655)
