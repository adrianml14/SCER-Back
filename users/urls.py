from django.urls import path

from users import views
from .views import csrf_cookie_view, register, login_view, CurrentUserView, BanderaListView  

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('csrf/', views.csrf_cookie_view, name='csrf'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('banderas/', BanderaListView.as_view(), name='bandera-list'),
]
