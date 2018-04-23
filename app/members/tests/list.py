import math

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from ..serializers import UserSerializer

__all__ = (
    'UserListTest',
)

User = get_user_model()


class UserListTest(APITestCase):
    URL = '/user/'
    USERNAME = 'test@gmail.com'
    PASSWORD = 'testpassword'
    FIRST_NAME = '수민'
    LAST_NAME = '박'
    PHONE_NUM = '01012345567'
    USER_COUNT = 13
    PAGE_SIZE = 3

    def setUp(self):
        # 유저 만들기
        for i in range(self.USER_COUNT):
            test_user_data = {
                'username': f'{i + 1}' + self.USERNAME,
                'password': self.PASSWORD,
                'confirm_password': self.PASSWORD,
                'first_name': self.FIRST_NAME,
                'last_name': self.LAST_NAME,
                'phone_num': self.PHONE_NUM,
            }
            User.objects.create_django_user(**test_user_data)

    def test_user_list(self):
        page_num = math.ceil(self.USER_COUNT / self.PAGE_SIZE)

        for i in range(int(page_num)):
            response = self.client.get(self.URL, {'page': i + 1, 'page_size': self.PAGE_SIZE})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertIsNotNone(response.data['count'], 'count')
            self.assertEqual(response.data['count'], self.USER_COUNT)

            if i < page_num - 1:
                self.assertIsNotNone(response.data['next'], 'next')
            if i > 0:
                self.assertIsNotNone(response.data['previous'], 'previous')

            self.assertEqual(response.data['results'],
                             UserSerializer(User.objects.all()[i * self.PAGE_SIZE:(i + 1) * self.PAGE_SIZE],
                                            many=True).data, )
