import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class APIFacebookBackend:

    def authenticate(self, request, access_token):
        """
        User access token을 사용해서
        GraphAPI의 'User'항목을 리턴
            (엔드포인트 'me'를 사용해서 access_token에 해당하는 사용자의 정보를 가져옴)
        :param user_access_token: 정보를 가져올 Facebook User access token
        :return: User정보 (dict)
        """
        params = {
            'access_token': access_token,
            'fields': ','.join([
                'id',
                'email',
                'first_name',
                'last_name',
                'picture.width(1024)',
            ])
        }
        response = requests.get('https://graph.facebook.com/v2.12/me', params)
        # 요청에 성공했을 때 (정상 응답)만 진행, 아닐경우 None반환

        if response.status_code == status.HTTP_200_OK:
            response_dict = response.json()
            # print('response.content: ')
            # print(response.content)

            # print('response_dict: ')
            # print(response_dict)

            response_dict = response.json()
            facebook_id = response_dict['id']
            first_name = response_dict['first_name']
            last_name = response_dict['last_name']

            # email은 기본공개정보가 아니기 때문에 유저마다 존재유무가 다름
            email = response_dict.get('email', None)

            user, _ = User.objects.get_or_create(
                username=facebook_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                signup_type=User.SIGNUP_TYPE_FACEBOOK
            )
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None