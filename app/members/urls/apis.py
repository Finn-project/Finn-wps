from django.urls import path, re_path

from ..apis import (
    UserListCreateAPIView,
    UserRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path('', UserListCreateAPIView.as_view()),
    path('<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view()),
]
