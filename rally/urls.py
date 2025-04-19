from django.urls import path
from .views import ComprarElementoView, ObtenerPresupuestoView, PilotoListView, CopilotoListView, CocheListView
from rally import views

urlpatterns = [
    path('pilotos/', PilotoListView.as_view(), name='pilotos'),
    path('copilotos/', CopilotoListView.as_view(), name='copilotos'),
    path('coches/', CocheListView.as_view(), name='coches'),
    path('presupuesto/', ObtenerPresupuestoView.as_view(), name='obtener_presupuesto'),
    path('comprar/<str:tipo>/<int:id_elemento>/', ComprarElementoView.as_view(), name='comprar_elemento'),
]


