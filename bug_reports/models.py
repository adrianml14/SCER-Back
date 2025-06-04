from django.db import models
from django.contrib.auth.models import User

class BugReport(models.Model):
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    resuelto = models.BooleanField(default=False)

    def __str__(self):
        return self.descripcion[:50] 
