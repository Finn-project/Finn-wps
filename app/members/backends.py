import requests
from django.contrib.auth import get_user_model
from django.core.files.base import File, ContentFile
from rest_framework import status

from members.models import UserProfileImages
from utils.image.file import download
from utils.image.resize import img_resize

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
            #
            # print('response_dict: ')
            # print(response_dict)

            facebook_id = response_dict['id']
            first_name = response_dict['first_name']
            last_name = response_dict['last_name']
            img_profile_url = response_dict['picture']['data']['url']

            # email은 기본공개정보가 아니기 때문에 유저마다 존재유무가 다름
            email = response_dict.get('email')

            # get_or_created -> update_or_created로 변경
            #                -> 다시 get_or_create로 회귀
            #              ( update_or_create를 하게되면 우리 서비스에서 입력한 정보,
            #                예를들면 로그인할 수 있는 메일계정이 담긴 정보가 사라져버림.
            #               * 중요도: 우리서비스 입력정보 > 페이스북에서 가져온 정보 )
            user, _ = User.objects.get_or_create(
                username=facebook_id,
                defaults={
                    # email이 기존 서비스내에 존재하는 지 검사해서 없으면 할당, 존재하면 None 입력
                    # (사실 아래 조건표현식에서 'email == None'을 빼도 되지만 뒤 조건에서 filter가 달렸기때문에
                    #  쿼리 최적화를 위해 이 조건을 그대로 남겨 둠)
                    'email': None if email is None or User.objects.filter(email=email).exists() else email,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )

            # (최초 로그인 user의 경우에만!)
            # Facebook에서 받아온 사진으로 img_profile 저장
            if user.is_facebook_user is False:
                # temp_file = download(img_profile_url)
                # file_name = '{facebook_id}.{ext}'.format(
                #     facebook_id=facebook_id,
                    # facebook_id='img_profile',
                    # ext='png',
                # )
                # user.img_profile.save(file_name, File(temp_file))

                response = requests.get(img_profile_url)
                binary_data = response.content
                img = UserProfileImages.objects.create(user=user)

                # img.img_profile.save('img_profile.png', File(temp_file))
                img.img_profile.save('img_profile.png', ContentFile(binary_data))
                # img.img_profile_28.save('img_profile_28.png', ContentFile(binary_data))
                # img.img_profile_225.save('img_profile_225.png', ContentFile(binary_data))

                user.is_facebook_user = True
                user.save()

            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
