from django.urls import path, include

app_name = 'apis'
urlpatterns = [
    path('members/', include('members.urls.apis')),
]
