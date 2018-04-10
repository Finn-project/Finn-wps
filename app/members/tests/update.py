from django.contrib.auth import get_user_model
from django.test.client import encode_multipart
from rest_framework.test import APITestCase

__all__ = (
    'UserUpdateTest',
)

User = get_user_model()


class UserUpdateTest(APITestCase):
    def setUp(self):
        # test user 생성
        test_user_info = {
            'username': 'test_user_01@gmail.com',
            'password': 'asdfqwer',
            'confirm_password': 'asdfqwer',
            'first_name': 'Park',
            'last_name': 'Boyoung',
            'phone_num': '010-1234-5678',
        }
        self.client.post('/user/', test_user_info)

    def test_user_update(self):
        """
        Method: POST
        일반회원이 업데이트 테스트
        :return:
        """

        # 미리 생성된 test user로 로그인 후 Header에 Token 값 넣기
        test_user_info = {'username': 'test_user_01@gmail.com', 'password': 'asdfqwer'}
        response = self.client.post('/user/login/', test_user_info)
        token = response.json()['token']
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token,
        )

        # User Update 요청 부분

        img_profile = open('../.static/iu.jpg', 'rb')

        request_contents = {
            'email': 'test_user_02@gmail.com',
            'password': 'asdfqwer1',
            'confirm_password': 'asdfqwer1',
            'first_name': '이유',
            'last_name': '아',
            'phone_num': '011-1111-1111',
            'img_profile': img_profile,
        }
        encoded_contents = encode_multipart('BoUnDaRyStRiNg', request_contents)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        user = User.objects.get(username='test_user_01@gmail.com')
        response = self.client.put(
            f'/user/{user.pk}/',
            encoded_contents,
            content_type=content_type,
        )
        img_profile.close()

        result = response.json()

        print(result)
