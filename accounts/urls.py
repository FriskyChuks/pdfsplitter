from django.urls import path

from .views import *

urlpatterns = [
    path('auth_login/',login_view, name='auth_login'),
    path('change_password/', change_password, name='change_password'),
    path('auth_logout/', logout_view, name='auth_logout'),
    path('search/', search_user, name='search'),
    path('reset_password/<int:id>/', reset_password, name='reset_password'),
]