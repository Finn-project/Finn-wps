from django.urls import path, re_path

from ..apis import (
    HouseListCreateAPIView,
    HouseRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('', HouseListCreateAPIView.as_view()),
    path('<int:pk>/', HouseRetrieveUpdateDestroyAPIView.as_view()),
]
