from django.db import models
from users.models import User

class Piloto(models.Model):
    nombre = models.CharField(max_length=255)
    bandera = models.URLField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    puntos_totales = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def actualizar_puntos_totales(self):
        total = sum(p.puntos for p in self.participacionrally_set.all())
        self.puntos_totales = total
        self.save(update_fields=['puntos_totales'])


class Copiloto(models.Model):
    nombre = models.CharField(max_length=255)
    bandera = models.URLField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    puntos_totales = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def actualizar_puntos_totales(self):
        total = sum(p.puntos for p in self.participacionrally_set.all())
        self.puntos_totales = total
        self.save(update_fields=['puntos_totales'])


class Coche(models.Model):
    modelo = models.CharField(max_length=255)
    imagen = models.URLField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    puntos_totales = models.IntegerField(default=0)

    def __str__(self):
        return self.modelo

    def actualizar_puntos_totales(self):
        total = sum(p.puntos for p in self.participacionrally_set.all())
        self.puntos_totales = total
        self.save(update_fields=['puntos_totales'])


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

    def calcular_puntos_por_posicion(self):
        tabla_puntos = {
            1: 25,
            2: 18,
            3: 15,
            4: 12,
            5: 10,
            6: 8,
            7: 6,
            8: 4,
            9: 2,
            10: 1
        }
        return tabla_puntos.get(self.posicion, 0)

    def save(self, *args, **kwargs):
        # Asigna automáticamente los puntos según la posición
        self.puntos = self.calcular_puntos_por_posicion()
        super().save(*args, **kwargs)

        # Actualiza los puntos totales acumulados de cada participante
        if self.piloto:
            self.piloto.actualizar_puntos_totales()
        if self.copiloto:
            self.copiloto.actualizar_puntos_totales()
        if self.coche:
            self.coche.actualizar_puntos_totales()



class FantasyTeam(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, default="Mi equipo")
    pilotos = models.ManyToManyField(Piloto, blank=True)
    copilotos = models.ManyToManyField(Copiloto, blank=True)
    coches = models.ManyToManyField(Coche, blank=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, default=1000000.00)
    puntos = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.user.username})"


class FantasyTeamRally(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rally = models.ForeignKey(Rally, on_delete=models.CASCADE)

    pilotos = models.ManyToManyField(Piloto, blank=True)
    copilotos = models.ManyToManyField(Copiloto, blank=True)
    coches = models.ManyToManyField(Coche, blank=True)

    puntos = models.IntegerField(default=0)  # calculado después de cada rally

    class Meta:
        unique_together = ('user', 'rally')

    def __str__(self):
        return f"{self.user.username} - {self.rally.nombre} - Puntos: {self.puntos}"

    def calcular_puntos_equipo(self):
        # Calcula los puntos totales del equipo fantasy para este rally
        puntos_pilotos = sum(p.puntos for p in self.pilotos.all())
        puntos_copilotos = sum(c.puntos for c in self.copilotos.all())
        puntos_coches = sum(co.puntos for co in self.coches.all())
        return puntos_pilotos + puntos_copilotos + puntos_coches

    def actualizar_puntos(self):
        self.puntos = self.calcular_puntos_equipo()
        self.save(update_fields=['puntos'])
