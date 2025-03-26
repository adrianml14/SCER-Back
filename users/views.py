from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from .models import User
from django.contrib.auth.hashers import make_password

@csrf_exempt
def register(request):
    # Si es una solicitud POST (para registrar el usuario)
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Verificar si el correo ya está registrado
        if User.objects.filter(email=email).exists():
            return HttpResponse("El correo ya está registrado", status=400)

        # Crear el usuario y almacenar la contraseña de forma segura
        user = User(name=name, email=email)
        user.password = make_password(password)  # Encriptar la contraseña
        user.save()

        # Responder con mensaje de éxito
        return HttpResponse("Registro exitoso", status=201)

    # Si es una solicitud GET, podemos devolver un formulario vacío o un mensaje indicando que es un registro
    elif request.method == "GET":
        return HttpResponse("Formulario de registro (GET)", status=200)

    return HttpResponse("Método no permitido", status=405)


@csrf_exempt  # Solo para pruebas, no recomendado en producción
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Buscar al usuario por correo electrónico
        try:
            # Buscar usuario por correo electrónico
            user = User.objects.get(email=email)
            
            # Autenticación manual: Verificar la contraseña del usuario
            if user.check_password(password):
                # Si la contraseña es correcta, hacer login
                login(request, user)
                return HttpResponse("Login exitoso", status=200)
            else:
                return HttpResponse("Contraseña incorrecta", status=401)
        except User.DoesNotExist:
            return HttpResponse("Usuario no encontrado", status=404)

    return HttpResponse("Método no permitido", status=405)
