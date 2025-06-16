import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from rally.models import FantasyTeam
from users.models import User, UsuarioRol, Rol
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@require_POST
@csrf_exempt
def register(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return JsonResponse({"error": "Todos los campos son obligatorios"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "El nombre de usuario ya está registrado"}, status=400)

        if len(password) < 6:
            return JsonResponse({"error": "La contraseña debe tener al menos 6 caracteres"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)

        # Crear equipo fantasy con presupuesto inicial
        FantasyTeam.objects.create(user=user, presupuesto=500000.00)

        return JsonResponse({"message": "Registro exitoso"}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Formato JSON inválido"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@ensure_csrf_cookie
def csrf_cookie_view(request):
    return JsonResponse({'detail': 'CSRF cookie set'})


@require_POST
@csrf_protect
def login_view(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"message": "Campos obligatorios"}, status=400)

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)  # Esto crea la sesión
            return JsonResponse({"message": "Login exitoso"})
        else:
            return JsonResponse({"message": "Credenciales inválidas"}, status=401)

    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rol = request.user.roles.first()
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "rol": rol.nombre if rol else None
        })

# cambiar roles usuario - VIP
class ToggleVIPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        rol_vip, _ = Rol.objects.get_or_create(nombre="VIP")
        rol_usuario, _ = Rol.objects.get_or_create(nombre="Usuario")

        # Obtener el rol actual
        rol_actual = user.roles.first()

        # Eliminar roles actuales
        UsuarioRol.objects.filter(usuario=user).delete()

        if rol_actual == rol_vip:
            UsuarioRol.objects.create(usuario=user, rol=rol_usuario)
            nuevo_rol = 'Usuario'
        else:
            UsuarioRol.objects.create(usuario=user, rol=rol_vip)
            nuevo_rol = 'VIP'

        return Response({
            "mensaje": f"Tu rol ha sido cambiado a {nuevo_rol}",
            "nuevo_rol": nuevo_rol
        })
    
# cambiar roles Usuario - Administrador
class ToggleAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        rol_admin, _ = Rol.objects.get_or_create(nombre="Administrador")
        rol_usuario, _ = Rol.objects.get_or_create(nombre="Usuario")

        rol_actual = user.roles.first()

        # Si NO es admin, requiere clave
        if rol_actual != rol_admin:
            clave_admin = request.data.get("clave")
            if clave_admin != "3313":
                return Response({
                    "mensaje": "Clave incorrecta. No tienes permiso para convertirte en administrador."
                }, status=403)

        # Eliminar todos los roles actuales
        UsuarioRol.objects.filter(usuario=user).delete()

        if rol_actual == rol_admin:
            UsuarioRol.objects.create(usuario=user, rol=rol_usuario)
            nuevo_rol = 'Usuario'
        else:
            UsuarioRol.objects.create(usuario=user, rol=rol_admin)
            nuevo_rol = 'Administrador'

        return Response({
            "mensaje": f"Tu rol ha sido cambiado a {nuevo_rol}",
            "nuevo_rol": nuevo_rol
        })
