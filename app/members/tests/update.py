import os
from django.contrib.auth import get_user_model
from django.test.client import encode_multipart
from rest_framework.test import APITestCase

from members.models import UserProfileImages

__all__ = (
    'UserUpdateTest',
)

User = get_user_model()


class UserUpdateTest(APITestCase):

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

    def test_user_update(self):
        """
        Method: POST
        일반회원이 업데이트 테스트
        :return:
        """

        # 미리 생성된 test user로 로그인 후 Header에 Token 값 넣기
        test_user_info = {'username': self.USERNAME, 'password': self.PASSWORD}
        response = self.client.post('/user/login/', test_user_info)
        token = response.json()['token']
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token,
        )

        # User Update 요청 부분
        img_profile = open('../.static/iu.jpg', 'rb')

        request_contents = {
            'email': 'test2@gmail.com',
            # 'password': 'asdfqwer1',
            # 'confirm_password': 'asdfqwer1',
            'first_name': '이유',
            'last_name': '아',
            'phone_num': '011-1111-1111',
            'img_profile': img_profile,
        }
        encoded_contents = encode_multipart('BoUnDaRyStRiNg', request_contents)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        user = User.objects.get(username='test@gmail.com')
        response = self.client.patch(
            f'/user/{user.pk}/',
            encoded_contents,
            content_type=content_type,
        )
        img_profile.close()
        result = response.json()

        # status_code 확인
        self.assertEqual(response.status_code, 200)

        # update 결과 response 확인
        self.assertEqual(result['username'], request_contents['email'])
        self.assertEqual(result['email'], request_contents['email'])
        self.assertEqual(result['first_name'], request_contents['first_name'])
        self.assertEqual(result['last_name'], request_contents['last_name'])
        self.assertEqual(result['phone_num'], request_contents['phone_num'])
        self.assertEqual(result['is_email_user'], True)
        self.assertEqual(result['is_facebook_user'], False)
        self.assertIsNotNone(result['images']['img_profile'])
        self.assertIsNotNone(result['images']['img_profile_28'])
        self.assertIsNotNone(result['images']['img_profile_225'])

        # update로 비밀변경 후 기존 비밀번호로 로그인 (실패)
        response = self.client.post('/user/login/', test_user_info)
        self.assertEqual(response.status_code, 400)

        # update로 비밀변경 후 변경된 비밀번호로 로그인 (성공)
        # request_contents2 = {
        #     'username': request_contents['email'],
        #     # 'password': request_contents['password'],
        #     'password': self.PASSWORD,
        # }
        # response = self.client.post('/user/login/', request_contents2)
        # self.assertEqual(response.status_code, 200)

        # image 저장 확인
        img = UserProfileImages.objects.get(user=user)
        self.assertTrue(os.path.isfile(img.img_profile.path))

        # print(type(img.img_profile))
        # print(img.img_profile_28.url)

        self.assertEqual(result['images']['img_profile'], img.img_profile.url)
        self.assertEqual(result['images']['img_profile_28'], img.img_profile_28.url)
        self.assertEqual(result['images']['img_profile_225'], img.img_profile_225.url)
