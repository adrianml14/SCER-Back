from django.urls import path
from .views import PilotoListView, CopilotoListView, CocheListView

urlpatterns = [
    path('pilotos/', PilotoListView.as_view(), name='pilotos'),
    path('copilotos/', CopilotoListView.as_view(), name='copilotos'),
    path('coches/', CocheListView.as_view(), name='coches'),
]
