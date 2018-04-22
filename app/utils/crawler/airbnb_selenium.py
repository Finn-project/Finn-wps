import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver

# import django
# django.setup()

# 한줄로 처리
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')


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

        # if soup.select_one('span._13nd2f7d > h1._1xu9tpch') is None:
        #     with open('.../test.html', 'wt') as f:
        #         f.write(html)
        #     print('test.html에 기록하고 종료')
        #     return
        with open('test.html', 'wt', encoding='utf8') as f:
            f.write(html)

        # 1) name
        name = soup.select_one('span._13nd2f7d > h1._1xu9tpch').get_text(strip=True)

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

        # 3) room, bed, bathroom, personnel
        span_list = soup.select('div._1thk0tsb > span._y8ard79')
        print(span_list)
        basic_info_list = []
        for span in span_list:
            text = span.get_text(strip=True)
            basic_info_list.append(text)
        print(basic_info_list)

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

        print(personnel)
        print(room)
        print(bed)
        print(bathroom)

        soup = BeautifulSoup(html, 'lxml')

        #                       neighborhood > div > div > div > div._e296pg > section > div._e296pg > div > div._1fmyluo4 > div > div > div > div:nth-child(9) > div:nth-child(2) > a
        #                       neighborhood > div > div > div > div._e296pg > section > div._e296pg > div > div._1fmyluo4 > div > div > div > div:nth-child(2) > a
        href = soup.select_one('div#neighborhood > div > div > div > div._e296pg > section > div._e296pg > div > div._1fmyluo4')
        # href = soup.select_one('dev._1fmyluo4 > div > div > div > div:nth-child(2) > a')
        # href = soup.select_one('dev._1fmyluo4 > div > div > div > div:nth-child(2) > a').get('href')
        print(href)
        # lat_lng = re.search('.*?=(.*?),(.*?)=', href)
        # lat = lat_lng.group(1)
        # lng = lat_lng.group(2)
        # print('lat')
        # print('lng')

        minimum_check_in_duration = 1,
        maximum_check_in_duration = 3,
        maximum_check_in_range = 90,
        price_per_night = 100000,
        country = ''
        city = ''
        district = ''
        dong = ''
        address1 = ''
        latitude = ''
        longitude = ''
        # disable_days = [
        #     '2014-01-01',
        #     '2014-02-01',
        #     '2014-03-01',
        #     '2014-04-01',
        # ],
        # amenities = [],
        # facilities = [1, 2, 3, 4, 5],

        result = {}
        return result

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

            print('---------------------------------------------')
            print(f'{city} 지역의 숙소를 크롤링 시작')
            print('---------------------------------------------')

            for num in range(num_of_pages):

                print('------------------------------------------------')
                print(f'{city} 지역의 숙소 검색결과 목록 중 "{num+1}" 페이지를 크롤링 중입니다..')
                print('------------------------------------------------')

                url = f'https://www.airbnb.co.kr/s/homes?query={city}&section_offset={num+1}'
                # response = requests.get(url)

                # with open('../test.html', 'wt') as f:
                #     f.write(html)
                # -> 동적으로 페이지가 구성되기 때문에 Selenium으로 불러와야함.

                self.driver.get(url)
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'lxml')

                house_info = {}
                itemListElement_list = soup.find('div', class_='_fhph4u').find_all('div', class_='_gig1e7')
                house_num = len(itemListElement_list)
                for i in itemListElement_list:
                    house_id_str = i.select_one('div > div > div').get('id')
                    house_id = house_id_str.split('-')[1]

                    print(f'숙소 {house_id}를 크롤링합니다.')
                    result = self.house_detail_crawling(house_id)
                    house_info[id] = result
                    break


if __name__ == '__main__':
    air = AirbnbCrawler(3)
    # air.house_page_crawling()
    air.house_detail_crawling(17563112)
    # air.house_detail_crawling(19350356)
