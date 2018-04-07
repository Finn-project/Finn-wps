import os
from django.conf import settings

from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Manager


# 다른 곳에서 아래의 CHOICES 속성을 참조하려고 할 때
# 모델 클래스 'User'와 'User = get_user_model'이 겹쳐서 import되지 않는 문제 발생
# -> 1. 아래처럼 class 밖으로 빼서 전역변수로 만듦.
#    2. 'User' 대신 'MyUser'로 네이밍

# SIGNUP_TYPE_EMAIL = 'e'
# SIGNUP_TYPE_FACEBOOK = 'f'
#
# SIGNUP_TYPE_CHOICES = (
#     (SIGNUP_TYPE_FACEBOOK, 'facebook'),
#     (SIGNUP_TYPE_EMAIL, 'email'),
# )


def dynamic_img_profile_path(instance, file_name):
    return f'user/user_{instance.id}/{file_name}'


class UserManager(DjangoUserManager):
    def create_django_user(self, *args, **kwargs):
        user = User.objects.create_user(
            username=kwargs.get('username'),
            email=kwargs.get('username'),
            password=kwargs.get('password'),
            first_name=kwargs.get('first_name'),
            last_name=kwargs.get('last_name'),
            phone_num=kwargs.get('phone_num', ''),
            # signup_type=SIGNUP_TYPE_EMAIL
            is_email_user=True,
        )
        # default profile_image 생성
        file = open('../.static/img_profile_default.png', 'rb').read()
        user.img_profile.save('img_profile.png', ContentFile(file))

        return user

    def create_facebook_user(self, *args, **kwargs):
        pass


class User(AbstractUser):
    file_path = os.path.join(settings.STATIC_DIR, 'img_profile_default.png')

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)

    img_profile = models.ImageField(upload_to=dynamic_img_profile_path, blank=True, default='')
    phone_num = models.CharField(max_length=20, blank=True)
    # signup_type = models.CharField(max_length=1, choices=SIGNUP_TYPE_CHOICES, default=SIGNUP_TYPE_EMAIL)
    is_facebook_user = models.BooleanField(default=False)
    is_email_user = models.BooleanField(default=False)

    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)

    is_host = models.BooleanField(default=False)

    objects = UserManager()


class HostManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_host=True)


class Host(User):
    objects = HostManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'{self.username} (호스트)'


class GuestManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_host=False)


class Guest(User):
    objects = GuestManager()

    class Meta:
        proxy = True

    def change_host(self):
        self.is_host = True
        self.save()

    def __str__(self):
        return f'{self.username} (게스트)'

