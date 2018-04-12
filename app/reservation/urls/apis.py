from django.urls import path

from ..apis.reservation import (
    ReservationCreateListView,
    ReservationRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('', ReservationCreateListView.as_view()),
    path('<int:pk>/', ReservationRetrieveUpdateDestroyView.as_view()),
]