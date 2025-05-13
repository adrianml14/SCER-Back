import random
import string
from django.shortcuts import render
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Liga(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    dueño = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ligas_propias')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    codigo_unico = models.CharField(max_length=5, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.codigo_unico:
            self.codigo_unico = self.generar_codigo()
        super().save(*args, **kwargs)

    def generar_codigo(self):
        while True:
            codigo = ''.join(random.choices(string.digits, k=5))
            if not Liga.objects.filter(codigo_unico=codigo).exists():
                return codigo

class ParticipacionLiga(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE, related_name='participantes')
    fecha_union = models.DateTimeField(auto_now_add=True)
    puntos = models.IntegerField(default=0)

    class Meta:
        unique_together = ('usuario', 'liga')

