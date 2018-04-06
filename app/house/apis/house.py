from rest_framework import permissions
from rest_framework.views import APIView

__all__ = (
    'HouseListCreateAPIView',
    'HouseRetrieveUpdateDestroyAPIView',
)


class HouseListCreateAPIView(APIView):
    def post(self, request):
        pass

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
