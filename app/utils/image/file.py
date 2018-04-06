from io import BytesIO

import magic
import requests


def download(url):
    # url로부터 다운받은 데이터를 BytesIO객체에 쓰고 리턴
    response = requests.get(url)
    binary_data = response.content
    temp_file = BytesIO()
    temp_file.write(binary_data)
    temp_file.seek(0)
    return temp_file


def get_buffer_ext(buffer):
    # BytesIO객체로부터 확장자를 알아내 리턴
    buffer.seek(0)
    mime_info = magic.from_buffer(buffer.read(), mime=True)
    buffer.seek(0)
    return mime_info.split('/')[-1]
