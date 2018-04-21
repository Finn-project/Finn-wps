from django.urls import path, re_path

from ..apis import (
    UserListCreateAPIView,
    UserRetrieveUpdateDestroyAPIView,
    UserLoginAuthTokenAPIView, UserLogoutAPIView,
    UserGetAuthTokenAPIView,
    AuthTokenForFacebookAccessTokenView,
    UserProfileImageDeleteAPIView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
)

urlpatterns = [
    # APIView
    # path('', UserListCreateAPIView.as_view()),
    # path('<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view()),

    # GenericView
    path('', UserListCreateView.as_view()),
    path('<int:pk>/', UserRetrieveUpdateDestroyView.as_view()),

    path('info/', UserGetAuthTokenAPIView.as_view()),
    path('<int:pk>/noimage/', UserProfileImageDeleteAPIView.as_view()),

    path('login/', UserLoginAuthTokenAPIView.as_view()),
    path('logout/', UserLogoutAPIView.as_view()),
    path('facebook-login/', AuthTokenForFacebookAccessTokenView.as_view()),
]
