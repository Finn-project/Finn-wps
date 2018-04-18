from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

__all__ = (
    'UserDeleteTest',
)

User = get_user_model()


class UserDeleteTest(APITestCase):

    URL = '/user/'
    USERNAME = 'test@gmail.com'
    PASSWORD = 'testpassword'
    FIRST_NAME = '보영'
    LAST_NAME = '박'
    PHONE_NUM = '01012345567'

    def setUp(self):
        # test user 생성
        test_user_info = {
            'username': self.USERNAME,
            'password': self.PASSWORD,
            'confirm_password': self.PASSWORD,
            'first_name': self.FIRST_NAME,
            'last_name': self.LAST_NAME,
            'phone_num': self.PHONE_NUM,
        }
        self.client.post(self.URL, test_user_info)

    def test_user_delete(self):
        """
        Method: POST
        일반회원이 회원탈퇴 테스트
        :return:
        """
        # test user pk
        user = User.objects.get(username=self.USERNAME)
        user_pk = user.pk

        # 미리 생성된 test user로 로그인 후 Header에 Token 값 넣기
        test_user_info = {'username': self.USERNAME, 'password': self.PASSWORD}
        response = self.client.post('/user/login/', test_user_info)
        token = response.json()['token']
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token,
        )

        # User Delete 요청 부분
        user = User.objects.get(username=test_user_info['username'])
        response = self.client.delete(
            f'/user/{user.pk}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # User Delete 후 로그인 검증
        test_user_info = {'username': self.USERNAME, 'password': self.PASSWORD}
        response = self.client.post('/user/login/', test_user_info)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # User Delete 후 회원 디테일 정보 조회 여부 검증
        response = self.client.get(f'/user/{user_pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # User Delete 후 User에서 filetering
        result = User.objects.filter(pk=user_pk)
        self.assertEqual(list(result), [])
