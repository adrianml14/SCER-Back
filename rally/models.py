from django.db import models
from users.models import User

class Piloto(models.Model):
    nombre = models.CharField(max_length=255)
    bandera = models.URLField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    puntos_totales = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Copiloto(models.Model):
    nombre = models.CharField(max_length=255)
    bandera = models.URLField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    puntos_totales = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Coche(models.Model):
    modelo = models.CharField(max_length=255)
    imagen = models.URLField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    puntos_totales = models.IntegerField(default=0)

    def __str__(self):
        return self.modelo

class Rally(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class ParticipacionRally(models.Model):
    rally = models.ForeignKey(Rally, on_delete=models.CASCADE)
    piloto = models.ForeignKey(Piloto, on_delete=models.SET_NULL, null=True, blank=True)
    copiloto = models.ForeignKey(Copiloto, on_delete=models.SET_NULL, null=True, blank=True)
    coche = models.ForeignKey(Coche, on_delete=models.SET_NULL, null=True, blank=True)
    equipo = models.CharField(max_length=255, blank=True)
    dorsal = models.CharField(max_length=10, blank=True)
    posicion = models.IntegerField(null=True, blank=True)
    puntos = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.rally.nombre} - {self.equipo}"

class FantasyTeam(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pilotos = models.ManyToManyField(Piloto, blank=True)
    copilotos = models.ManyToManyField(Copiloto, blank=True)
    coches = models.ManyToManyField(Coche, blank=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, default=1000000.00)

    def __str__(self):
        return f"Equipo de {self.user.username}"
