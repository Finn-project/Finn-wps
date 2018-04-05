import os
from django.conf import settings
from django.conf.global_settings import STATIC_ROOT

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Manager

SIGNUP_TYPE_EMAIL = 'e'
SIGNUP_TYPE_FACEBOOK = 'f'

SIGNUP_TYPE_CHOICES = (
    (SIGNUP_TYPE_FACEBOOK, 'facebook'),
    (SIGNUP_TYPE_EMAIL, 'email'),
)


def dynamic_img_profile_path(instance, file_name):
    return f'user/user_{instance.id}/{file_name}'


class User(AbstractUser):
    file_path = os.path.join(settings.STATIC_DIR, 'img_profile_default.png')

    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=False, null=True)

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
    is_customer = models.BooleanField(default=False)


class HostManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_host=True)


class Host(User):
    objects = HostManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'{self.username} (판매자)'


class CustomerManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_customer=True)


class Customer(User):
    objects = CustomerManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'{self.username} (고객)'
