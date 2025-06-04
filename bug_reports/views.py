from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BugReport
from rest_framework.permissions import IsAuthenticated
from .serializer import BugReportSerializer

class ReporteBugView(APIView):
    def post(self, request):
        serializer = BugReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': 'Reporte enviado correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GestionBugsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, bug_id=None):
        if bug_id is None:
            # Obtener todos
            bugs = BugReport.objects.all().order_by('-fecha')
            serializer = BugReportSerializer(bugs, many=True)
            return Response(serializer.data)
        else:
            # Obtener bug individual (opcional)
            bug = get_object_or_404(BugReport, id=bug_id)
            serializer = BugReportSerializer(bug)
            return Response(serializer.data)

    def delete(self, request, bug_id):
        bug = get_object_or_404(BugReport, id=bug_id)
        bug.delete()
        return Response({'mensaje': 'Reporte eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, bug_id):
        bug = get_object_or_404(BugReport, id=bug_id)
        nuevo_estado = request.data.get("resuelto")

        if nuevo_estado is None:
            return Response({'error': 'Falta el campo "resuelto"'}, status=status.HTTP_400_BAD_REQUEST)

        bug.resuelto = bool(nuevo_estado)
        bug.save()

        return Response({'mensaje': f'Bug marcado como {"resuelto" if bug.resuelto else "no resuelto"}'})
