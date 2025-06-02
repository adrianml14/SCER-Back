from rest_framework import serializers
from .models import User, Bandera

class BanderaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bandera
        fields = ['id', 'nombre', 'imagen_url']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    bandera = BanderaSerializer(read_only=True)
    bandera_id = serializers.PrimaryKeyRelatedField(
        queryset=Bandera.objects.all(), write_only=True, source='bandera', required=False
    )

    rol = serializers.CharField(source='rol_nombre', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'bandera', 'bandera_id', 'rol')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value


    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
