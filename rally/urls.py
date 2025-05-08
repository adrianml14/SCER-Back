from django.urls import path
from .views import CambiarNombreEquipoView, ComprarElementoView, MisCochesView, MisCopilotosView, MisPilotosView, ObtenerNombreEquipoView, ObtenerPresupuestoView, PilotoListView, CopilotoListView, CocheListView, VenderElementoView
from rally import views

urlpatterns = [
    path('pilotos/', PilotoListView.as_view(), name='pilotos'),
    path('copilotos/', CopilotoListView.as_view(), name='copilotos'),
    path('coches/', CocheListView.as_view(), name='coches'),
    
    path('presupuesto/', ObtenerPresupuestoView.as_view(), name='obtener_presupuesto'),

    # comprar y vender
    path('comprar/<str:tipo>/<int:id_elemento>/', ComprarElementoView.as_view(), name='comprar_elemento'),
    path('vender/<str:tipo>/<int:id_elemento>/', VenderElementoView.as_view(), name='vender_elemento'),
    
    # urls para devolver el equipo fantasy
    path('mis-pilotos/', MisPilotosView.as_view(), name='mis-pilotos'),
    path('mis-copilotos/', MisCopilotosView.as_view(), name='mis-copilotos'),
    path('mis-coches/', MisCochesView.as_view(), name='mis-coches'),

    # cambiar nombre del equipo
    path('cambiar-nombre-equipo/', CambiarNombreEquipoView.as_view(), name='cambiar-nombre-equipo'),
    path('nombre-equipo/', ObtenerNombreEquipoView.as_view(), name='nombre-equipo'),

]


