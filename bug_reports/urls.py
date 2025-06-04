from django.urls import path
from .views import ReporteBugView

urlpatterns = [
    path('report/', ReporteBugView.as_view(), name='reporte_bug'),
]
