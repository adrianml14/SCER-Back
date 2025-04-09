from rest_framework import generics
from .models import Piloto, Copiloto, Coche
from .serializer import PilotoSerializer, CopilotoSerializer, CocheSerializer

class PilotoListView(generics.ListAPIView):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer

class CopilotoListView(generics.ListAPIView):
    queryset = Copiloto.objects.all()
    serializer_class = CopilotoSerializer

class CocheListView(generics.ListAPIView):
    queryset = Coche.objects.all()
    serializer_class = CocheSerializer
