from django.urls import path
from .views import CambiarNombreEquipoView, ClasificacionPorRallyView, ComprarElementoView, HistoricoCocheView, HistoricoCopilotoView, HistoricoPilotoView, HistoricoUsuarioView, MisCochesView, MisCopilotosView, MisEquiposPorRallyView, MisPilotosView, ObtenerNombreEquipoView, ObtenerPresupuestoView, PilotoListView, CopilotoListView, CocheListView, VenderElementoView
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

    # historico de equipos en rallyes
    path('fantasy/rally/mis-equipos/', MisEquiposPorRallyView.as_view(), name='mis_equipos_rally'),

    path('historico/piloto/<int:piloto_id>/', HistoricoPilotoView.as_view(), name='historico_piloto'),
    path('historico/copiloto/<int:copiloto_id>/', HistoricoCopilotoView.as_view(), name='historico_copiloto'),
    path('historico/coche/<int:coche_id>/', HistoricoCocheView.as_view(), name='historico_coche'),
    
    # clasificación por rally de 
    path('clasificacion-por-rally/', ClasificacionPorRallyView.as_view(), name='clasificacion_por_rally'),

    #historico de cada equipo y puntos que tuvo el usuario en un equipo
    path('historico-usuario/', HistoricoUsuarioView.as_view(), name='historico_usuario'),

]


