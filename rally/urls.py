from django.urls import path
from .views import PilotoListView, CopilotoListView, CocheListView, obtener_presupuesto
from rally import views

urlpatterns = [
    path('pilotos/', PilotoListView.as_view(), name='pilotos'),
    path('copilotos/', CopilotoListView.as_view(), name='copilotos'),
    path('coches/', CocheListView.as_view(), name='coches'),
    path('presupuesto/', obtener_presupuesto, name='presupuesto'),
    path('comprar/<str:tipo>/<int:id_elemento>/', views.comprar_elemento, name='comprar_elemento'),
]

