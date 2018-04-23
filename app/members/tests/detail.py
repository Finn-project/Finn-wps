import math

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

__all__ = (
    'UserDetailTest',
)

User = get_user_model()


class UserDetailTest(APITestCase):
    URL = '/user/'
    USERNAME = 'test@gmail.com'
    PASSWORD = 'testpassword'
    FIRST_NAME = '수민'
    LAST_NAME = '박'
    PHONE_NUM = '01012345567'
    USER_COUNT = 10

    def test_user_detail(self):
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

        response = self.client.get(self.URL + '7/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_data = response.data

        self.assertEqual(user_data['pk'], 7)
        self.assertEqual(user_data['username'], '7' + self.USERNAME)
        self.assertEqual(user_data['email'], '7' + self.USERNAME)
        self.assertEqual(user_data['first_name'], self.FIRST_NAME)
        self.assertEqual(user_data['last_name'], self.LAST_NAME)
        self.assertEqual(user_data['phone_num'], self.PHONE_NUM)
        self.assertEqual(user_data['is_host'], False)
        self.assertEqual(user_data['is_email_user'], True)
        self.assertEqual(user_data['is_facebook_user'], False)
