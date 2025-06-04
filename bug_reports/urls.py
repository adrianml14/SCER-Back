from django.urls import path
from .views import ReporteBugView, GestionBugsView

urlpatterns = [
    path('report/', ReporteBugView.as_view(), name='reporte_bug'),
    path('bugs/', GestionBugsView.as_view(), name='listar_bugs'),  # GET para obtener todos
    path('bugs/<int:bug_id>/', GestionBugsView.as_view(), name='detalle_bug'),  # GET, DELETE y PATCH para uno
]
