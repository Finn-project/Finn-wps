import json
import re

import requests
from bs4 import BeautifulSoup


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
        url = 'https://www.airbnb.co.kr/s/homes?query=서울&section_offset=2'
        headers = {
            # 'cache-control': "no-cache",
            # 'user-agent': 'Mozilla/5.0',
            # 'postman-token': '3bef0069-9515-446e-93b7-3bb37a1e8a9b',
            # 'host': 'www.airbnb.co.kr',
            # 'accept': '*/*',
            # 'accept-encoding': 'gzip, deflate',
            'cookie': '__svt=1381; cache_state=0; bev=1523934971_5ussJFyJsy%2BcIwMA; _csrf_token=V4%24.airbnb.co.kr%24G6i45M0XMrs%24reAsEi8IPWdU9YJsn2apAPDEIOtNCuY26kcvWPawU70%3D; jitney_client_session_id=2f0abc70-0be3-4f8d-aac3-84363faa4a73; jitney_client_session_created_at=1523957423; jitney_client_session_updated_at=1523957423; _user_attributes=%7B%22curr%22%3A%22KRW%22%2C%22guest_exchange%22%3A1072.3055650000001%2C%22device_profiling_session_id%22%3A%221523934971--2a4ffad382218d61b920a404%22%2C%22giftcard_profiling_session_id%22%3A%221523957424--c718f2fe50a984671b19354d%22%2C%22reservation_profiling_session_id%22%3A%221523957424--48f5ec024f0477b119d21220%22%7D; flags=268697600; dtc_exp=1; 9f2398a3e=control; b3b78300e=control; 65e98c419=control; a8f0b01c0=control; 4b522145b=treatment',
        }

        # response = self.r.get(url, headers=headers)
        response = requests.get(url, headers=headers)
        source = response.text

        print(response.status_code)
        # print(result)

        # soup = BeautifulSoup(response.text, 'lxml')
        # soup.select_one('type')
        # soup.find('script', ='fe17d374-766e-4399-a759-c9b2ce60911c')

        bootstrap_data = re.search(r'data-hypernova-key="spaspabundlejs" data-hypernova-id=".*?"><!--(.*?)--></script>', source)
        # print(bootstrap_data.groups(1)[0:10])
        bootstrap_json = json.loads(bootstrap_data.group(1))

        listing_list = \
        bootstrap_json['bootstrapData']['reduxData']['exploreTab']['response']['explore_tabs'][0]['sections'][0][
            'listings']
        print(listing_list)
        print(type(listing_list))
        for i in range(len(listing_list)):
            print(listing_list[i])


airbnb = AirbnbCrawler()
airbnb.get_bootstrapdata()