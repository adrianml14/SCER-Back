from django.urls import path

from users import views
from .views import csrf_cookie_view, register, login

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('csrf/', views.csrf_cookie_view, name='csrf'), 
]
