from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

__all__ = (
    'UserDeleteTest',
)

User = get_user_model()


class UserDeleteTest(APITestCase):

    def test_user_delete(self):
        pass
