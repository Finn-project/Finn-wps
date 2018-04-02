from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    SIGNUP_TYPE_EMAIL = 'e'
    SIGNUP_TYPE_FACEBOOK = 'f'

    SIGNUP_TYPE_CHOICES = (
        (SIGNUP_TYPE_FACEBOOK, 'facebook'),
        (SIGNUP_TYPE_EMAIL, 'email'),
    )
    username = models.EmailField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=False)

    img_profile = models.ImageField(upload_to='user', blank=True)
    signup_type = models.CharField(max_length=1, choices=SIGNUP_TYPE_CHOICES)

    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
