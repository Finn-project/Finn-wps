from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    UserCreateSerializer,
    UserSerializer,
)

__all__ = (
    'SignUpView',
)


class SignUpView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)
