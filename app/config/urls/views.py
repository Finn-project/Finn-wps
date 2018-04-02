from django.urls import path

from ..views import view_index

urlpatterns = [
    path('', view_index)
]
