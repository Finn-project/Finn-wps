from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username=settings.SUPERUSER_USERNAME).exists():
            User.objects.create_superuser(
                username=settings.SUPERUSER_USERNAME,
                password=settings.SUPERUSER_PASSWORD,
                email=settings.SUPERUSER_EMAIL,
            )
        ios_test_user = {
            'username': 'iostest@gmail.com',
            'password': 'iostestpw',
            'first_name': '보영',
            'last_name': '박',
            'phone_num': '01012345678'
        }
        if not User.objects.filter(username=ios_test_user.get('username')):
            User.objects.create_user(
                username=ios_test_user.get('username'),
                email=ios_test_user.get('username'),
                password=ios_test_user.get('password'),
                first_name=ios_test_user.get('first_name'),
                last_name=ios_test_user.get('last_name'),
                phone_num=ios_test_user.get('phone_num'),
                is_email_user=True,
            )

        fds_test_user = {
            'username': 'fdstest@gmail.com',
            'password': 'fdstestpw',
            'first_name': '이유',
            'last_name': '아',
            'phone_num': '01012345678'
        }
        if not User.objects.filter(username=fds_test_user.get('username')):
            User.objects.create_user(
                username=fds_test_user.get('username'),
                email=fds_test_user.get('username'),
                password=fds_test_user.get('password'),
                first_name=fds_test_user.get('first_name'),
                last_name=fds_test_user.get('last_name'),
                phone_num=fds_test_user.get('phone_num'),
                is_email_user=True,
            )
