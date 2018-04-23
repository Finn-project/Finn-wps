from django.urls import path

from ..apis.reservation import (
    ReservationListCreateView,
    ReservationRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('', ReservationListCreateView.as_view()),
    path('<int:pk>/', ReservationRetrieveUpdateDestroyView.as_view()),
]