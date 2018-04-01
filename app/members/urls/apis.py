from django.urls import path

from ..apis import (
    SignUpView
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup')
]
