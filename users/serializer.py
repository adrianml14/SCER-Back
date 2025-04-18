from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Para asegurar que la contraseña no se pueda leer

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')  # Usamos 'username' en lugar de 'name'

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
