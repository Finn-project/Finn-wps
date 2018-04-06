from rest_framework import permissions
from rest_framework.views import APIView

__all__ = (
    'HouseListCreateAPIView',
    'HouseRetrieveUpdateDestroyAPIView',
)


class HouseListCreateAPIView(APIView):
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

    def get(self, request):
        pass


class HouseRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request):
        pass

    def put(self, request):
        pass

    def delete(self, request):
        pass
