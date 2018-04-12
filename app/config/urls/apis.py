from django.urls import path, include

app_name = 'apis'
urlpatterns = [
    path('user/', include('members.urls.apis')),
    path('house/', include('house.urls.apis')),
    path('reservation/', include('reservation.urls.apis')),
]
