from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    # Aseguramos que la contraseña solo se puede escribir, pero no se puede leer
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User  # El modelo que se va a serializar
        fields = ('id', 'name', 'email', 'password')  # Los campos a serializar

    # Sobrescribimos el método create para encriptar la contraseña
    def create(self, validated_data):
        # Extraemos la contraseña antes de crear el usuario
        password = validated_data.pop('password', None)
        
        # Creamos el usuario con los demás campos
        user = User.objects.create(**validated_data)

        # Establecemos la contraseña (encriptándola)
        if password:
            user.set_password(password)
            user.save()

        return user
