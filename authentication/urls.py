from django.urls import path
from .views import UserProfileView, user_statistics

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/statistics/', user_statistics, name='user-statistics'),
]