from django.urls import path
from .views import profile_view, profile_edit_view

app_name = 'account'

urlpatterns = [
    path('mypage/', profile_view, name='profile'),
    path('mypage/edit/', profile_edit_view, name='edit'),
]
