from django.urls import path, include

app_name = 'apis'
urlpatterns = [
    path('user/', include('members.urls.apis')),
]
