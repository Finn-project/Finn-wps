import random

from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .apis import UserRetrieveUpdateDestroyAPIView, UserSerializer

User = get_user_model()


class UserSignupTest(APITestCase):

    def test_user_signup(self):
        """
        Method: POST
        일반회원이 회원가입 테스트
        :return:
        """
        test_user_info = {
            'username': 'test_user_01@gmail.com',
            'password': 'asdfqwer',
            'confirm_password': 'asdfqwer',
            'first_name': 'Park',
            'last_name': 'Boyoung',
            'phone_num': '010-1234-5678',
        }

        response = self.client.post(
            '/user/',
            test_user_info,
        )
        result = response.json()

        # status_code 확인
        self.assertEqual(response.status_code, 200)

        # Signup 요청의 내용과 response의 내용 일치 확인
        self.assertEqual(result['user']['username'], test_user_info['username'])
        self.assertEqual(result['user']['first_name'], test_user_info['first_name'])
        self.assertEqual(result['user']['last_name'], test_user_info['last_name'])
        self.assertEqual(result['user']['phone_num'], test_user_info['phone_num'])

        # user 객체가 정상적으로 생성되었는지 확인
        user = User.objects.get(username=test_user_info['username'])
        self.assertEqual(user.username, test_user_info['username'])
        self.assertEqual(user.first_name, test_user_info['first_name'])
        self.assertEqual(user.last_name, test_user_info['last_name'])
        self.assertEqual(user.phone_num, test_user_info['phone_num'])
        self.assertEqual(user.check_password(test_user_info['password']), True)
        self.assertEqual(user.is_email_user, True)
        self.assertEqual(user.is_facebook_user, False)
        self.assertEqual(user.is_host, False)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_staff, False)
        self.assertIsNotNone(user.created_date)
        self.assertIsNotNone(user.modified_date)

        # host 전환 후 인증 되는지 검사
        user.is_host = True
        user.save()
        self.assertEqual(user, authenticate(
            username=test_user_info['username'],
            password=test_user_info['password'],
        ))

        # user 정보 출력해서 직접 확인
        # print(UserSerializer(user).data)


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


class UserListTest(APITestCase):

    MODEL = User
    VIEW = UserRetrieveUpdateDestroyAPIView
    PATH = '/user/'
    PAGINATION_COUNT = 25

    def test_user_list_count(self):
        num = random.randrange(1, 30)
        # for i in range(num):
            # User.objects.create()

    def test_artist_list_pagination(self):
        pass


class UserDetailTest(APITestCase):

    def test_user_detail(self):
        pass


class UserDeleteTest(APITestCase):

    def test_user_delete(self):
        pass


class UserUpdateTest(APITestCase):

    def test_user_update(self):
        pass
