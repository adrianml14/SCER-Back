from django.db import models
from users.models import User

class Rally(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre

class Piloto(models.Model):
    usuarios = models.ManyToManyField(User, related_name='pilotos')  # Relación Many-to-Many con User
    nombre = models.CharField(max_length=255)  # Agregar el nombre directamente en el modelo Piloto
    bandera = models.URLField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre

class Copiloto(models.Model):
    usuarios = models.ManyToManyField(User, related_name='copilotos')  # Relación Many-to-Many con User
    nombre = models.CharField(max_length=255)  # Agregar el nombre directamente en el modelo Copiloto
    bandera = models.URLField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre

class Coche(models.Model):
    marca_modelo = models.CharField(max_length=100)
    clase = models.CharField(max_length=50)
    icono_url = models.URLField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.marca_modelo} ({self.clase})"

class Participante(models.Model):
    rally = models.ForeignKey(Rally, on_delete=models.CASCADE, related_name="participantes")
    dorsal = models.CharField(max_length=10)
    piloto = models.ForeignKey(Piloto, on_delete=models.CASCADE)
    copiloto = models.ForeignKey(Copiloto, on_delete=models.SET_NULL, null=True, blank=True)
    coche = models.ForeignKey(Coche, on_delete=models.SET_NULL, null=True)
    equipo = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.rally.nombre} - {self.dorsal} - Piloto: {self.piloto.nombre} - Copiloto: {self.copiloto.nombre if self.copiloto else 'Sin Copiloto'}"
