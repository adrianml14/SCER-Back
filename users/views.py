import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError

from rally.models import FantasyTeam
from users.models import User


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

        user = User(username=username, email=email)  # Usé 'email' y 'username' para crear el usuario
        user.set_password(password)
        user.save()

        # Crear equipo de fantasía con presupuesto inicial
        FantasyTeam.objects.create(user=user, presupuesto=1000000.00)

        return JsonResponse({"message": "Registro exitoso"}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Formato JSON inválido"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@ensure_csrf_cookie
def csrf_cookie_view(request):
    return JsonResponse({'detail': 'CSRF cookie set'})

@login_required
def current_user(request):
    return JsonResponse({
        "username": request.user.username,
        "email": request.user.email,
    })


@require_POST
@csrf_exempt
def login_view(request):
    from django.contrib.auth import login as django_login
    import json

    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"message": "Todos los campos son obligatorios"}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Inicia sesión si quieres mantener sesión también
            django_login(request, user)

            # Obtiene o crea el token
            token, _ = Token.objects.get_or_create(user=user)

            return JsonResponse({
                "message": "Login exitoso",
                "token": token.key,
                "username": user.username
            }, status=200)
        else:
            return JsonResponse({"message": "Credenciales inválidas"}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({"message": "Formato JSON inválido"}, status=400)

    except Exception as e:
        return JsonResponse({"message": f"Error del servidor: {str(e)}"}, status=500)
