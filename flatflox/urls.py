# urls.py
from django.urls import path
from .views import login_user, signup_user, paid_guest, create_pg, get_working_cities

urlpatterns = [
    path('login/', login_user, name='login'),
    path('signup/', signup_user, name='signup'),
    path('paid_guest/', paid_guest, name='paid_guest'),
    path('create_pg/', create_pg, name='create_pg'),
    path('get_working_cities/', get_working_cities, name='get_working_cities'),
]
