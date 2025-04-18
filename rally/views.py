from rest_framework import generics
from .models import Piloto, Copiloto, Coche, FantasyTeam
from .serializer import PilotoSerializer, CopilotoSerializer, CocheSerializer
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

class PilotoListView(generics.ListAPIView):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer

class CopilotoListView(generics.ListAPIView):
    queryset = Copiloto.objects.all()
    serializer_class = CopilotoSerializer

class CocheListView(generics.ListAPIView):
    queryset = Coche.objects.all()
    serializer_class = CocheSerializer


@login_required
def obtener_presupuesto(request):
    user = request.user
    try:
        equipo = FantasyTeam.objects.get(user=user)
        return JsonResponse({'presupuesto': equipo.presupuesto})
    except FantasyTeam.DoesNotExist:
        return JsonResponse({'error': 'No se encontró el equipo'}, status=404)
    

@login_required
def comprar_elemento(request, tipo: str, id_elemento: int):
    user = request.user

    try:
        equipo = FantasyTeam.objects.get(user=user)

        # Imprimir el presupuesto actual antes de la compra (para depuración)
        print(f"Presupuesto antes de la compra: {equipo.presupuesto}")

        # Obtener el precio y la entidad según el tipo de elemento
        if tipo == 'piloto':
            elemento = Piloto.objects.get(id=id_elemento)
        elif tipo == 'copiloto':
            elemento = Copiloto.objects.get(id=id_elemento)
        elif tipo == 'coche':
            elemento = Coche.objects.get(id=id_elemento)
        else:
            return JsonResponse({'error': 'Tipo de elemento no válido'}, status=400)

        # Verificar si el usuario tiene suficiente presupuesto
        if equipo.presupuesto < elemento.precio:
            return JsonResponse({'error': 'No tienes suficiente presupuesto'}, status=400)

        # Restar el presupuesto
        equipo.presupuesto -= elemento.precio
        equipo.save()

        # Imprimir el presupuesto después de la compra (para depuración)
        print(f"Presupuesto después de la compra: {equipo.presupuesto}")

        # Añadir el elemento al equipo
        if tipo == 'piloto':
            equipo.pilotos.add(elemento)
        elif tipo == 'copiloto':
            equipo.copilotos.add(elemento)
        elif tipo == 'coche':
            equipo.coches.add(elemento)

        return JsonResponse({'mensaje': f'{tipo.capitalize()} comprado correctamente'}, status=200)

    except FantasyTeam.DoesNotExist:
        return JsonResponse({'error': 'Equipo no encontrado'}, status=404)
    except Piloto.DoesNotExist:
        return JsonResponse({'error': 'Piloto no encontrado'}, status=404)
    except Copiloto.DoesNotExist:
        return JsonResponse({'error': 'Copiloto no encontrado'}, status=404)
    except Coche.DoesNotExist:
        return JsonResponse({'error': 'Coche no encontrado'}, status=404)
