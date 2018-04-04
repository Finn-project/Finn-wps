from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Manager


class User(AbstractUser):
    SIGNUP_TYPE_EMAIL = 'e'
    SIGNUP_TYPE_FACEBOOK = 'f'

    SIGNUP_TYPE_CHOICES = (
        (SIGNUP_TYPE_FACEBOOK, 'facebook'),
        (SIGNUP_TYPE_EMAIL, 'email'),
    )
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=False, null=True)

    img_profile = models.ImageField(upload_to='user')
    signup_type = models.CharField(max_length=1, choices=SIGNUP_TYPE_CHOICES, default=SIGNUP_TYPE_EMAIL)
    phone_num = models.CharField(max_length=20, null=True)

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
