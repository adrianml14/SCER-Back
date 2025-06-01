from django.urls import path
from .views import ClasificacionGeneralView, GestionParticipantesView, LigaListCreateView, ParticipacionLigaCreateView, MisLigasView, unirse_por_codigo

urlpatterns = [
    path('', LigaListCreateView.as_view(), name='listar-crear-ligas'),
    path('unirse/', ParticipacionLigaCreateView.as_view(), name='unirse-liga'),
    path('unirse-codigo/', unirse_por_codigo, name='unirse_por_codigo'),  # <-- esta es nueva
    path('mis-ligas/', MisLigasView.as_view(), name='mis-ligas'),
    path('<int:liga_id>/participantes/', GestionParticipantesView.as_view(), name='gestionar_participantes'),
    path('clasificacion-general/', ClasificacionGeneralView.as_view(), name='clasificacion-general'),
]