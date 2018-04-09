from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from ..serializers import UserSerializer

__all__ = (
    'UserLoginLogoutTest',
)

User = get_user_model()


class UserLoginLogoutTest(APITestCase):

    # UserLoginLogoutTest에서
    # (*setUp에서 대문자 U로 써야 제대로 작동)
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

    def test_user_login(self):
        """
        Method: POST
        일반회원이 로그인 테스트
        :return:
        """

        # 생성한 test user로 로그인
        test_user_info = {
            'username': 'test_user_01@gmail.com',
            'password': 'asdfqwer',
        }
        response = self.client.post(
            '/user/login/',
            test_user_info,
        )
        result = response.json()

        # status_code 확인
        self.assertEqual(response.status_code, 200)

        # Login으로 Token이 제대로 발급되었는지 확인
        self.assertEqual(result['token'], Token.objects.get(user_id=result['user']['pk']).key)

        # Login으로 user 정보가 제대로 return 되었는지 확인
        user = User.objects.get(username=test_user_info['username'])
        self.assertEqual(result['user'], UserSerializer(user).data)

    def test_user_logout(self):
        """
        Method: POST
        일반회원이 로그아웃 테스트
        :return:
        """
        # 생성한 test user로 로그인
        test_user_info = {'username': 'test_user_01@gmail.com', 'password': 'asdfqwer'}
        response = self.client.post('/user/login/', test_user_info)

        # 로그인 후 받은 token으로 로그아웃
        token = response.json()['token']
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token,
        )
        response = self.client.post('/user/logout/')

        # status_code 확인
        self.assertEqual(response.status_code, 200)

        # Response message 확인
        self.assertEqual(response.data, '해당 유저가 로그아웃되었습니다.')
