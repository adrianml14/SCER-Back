from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Guardará la contraseña encriptada

    def save(self, *args, **kwargs):
        """Encripta la contraseña antes de guardar el usuario"""
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def check_password(self, raw_password):
        return django_check_password(raw_password, self.password)

    def __str__(self):
        return self.name
