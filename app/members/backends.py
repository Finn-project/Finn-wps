from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import User

User = get_user_model()


class UserCreateBackend:
    def validate_email(self, email):
        is_exists = User.objects.filter(email=email).exists()
        if is_exists:
            raise serializers.ValidationError('이미 존재 하는 메일 입니다.')

    def validate_password(self, password, confirm_password):
        if not password or not confirm_password:
            raise serializers.ValidationError('비밀번호와 비밀번호 확인란을 적어 주십시오.')

        if password != confirm_password:
            raise serializers.ValidationError('비밀번호가 일치하지 않습니다.')

    def authenticate(self, request,
                     email=None,
                     password=None,
                     confirm_password=None,
                     first_name=None,
                     last_name=None,
                     ):
        self.validate_email(email)
        self.validate_password(password=password, confirm_password=confirm_password)

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                signup_type=User.SIGNUP_TYPE_EMAIL,
            )

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
