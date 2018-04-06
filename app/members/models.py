import os
from django.conf import settings

from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Manager
from rest_framework import status

from utils.exception.custom_exception import CustomException

SIGNUP_TYPE_EMAIL = 'e'
SIGNUP_TYPE_FACEBOOK = 'f'

SIGNUP_TYPE_CHOICES = (
    (SIGNUP_TYPE_FACEBOOK, 'facebook'),
    (SIGNUP_TYPE_EMAIL, 'email'),
)


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
            signup_type=SIGNUP_TYPE_EMAIL
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

    # 1) 기본방법 사용
    # img_profile = models.ImageField(upload_to=dynamic_img_profile_path, blank=True, default='/static/iu.jpg')

    # 2) os.path.join 활용
    # file_path = os.path.join(STATIC_ROOT, 'iu.jpg')
    # img_profile = models.ImageField(upload_to=dynamic_img_profile_path, blank=True, default=file_path)

    # 3)
    # file_path = os.path.join(settings.STATIC_ROOT, 'iu.jpg')
    # file = open(file_path, 'rb').read()

    img_profile = models.ImageField(upload_to=dynamic_img_profile_path, blank=True, default='')
    phone_num = models.CharField(max_length=20, blank=True)
    signup_type = models.CharField(max_length=1, choices=SIGNUP_TYPE_CHOICES, default=SIGNUP_TYPE_EMAIL)

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
