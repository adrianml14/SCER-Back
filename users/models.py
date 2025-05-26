from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models

# Tabla de roles
class Rol(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre

# Tabla intermedia: relación muchos a muchos entre usuarios y roles
class UsuarioRol(models.Model):
    usuario = models.ForeignKey('User', on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'rol')

    def __str__(self):
        return f'{self.usuario.username} - {self.rol.nombre}'

# User manager personalizado
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("El usuario debe tener un email")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Modelo de usuario
class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)

    bandera = models.ForeignKey(
        'Bandera',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )

    # Relación muchos a muchos con roles a través de la tabla intermedia
    roles = models.ManyToManyField(
        Rol,
        through='UsuarioRol',
        related_name='usuarios'
    )

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

# Modelo bandera
class Bandera(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    imagen_url = models.URLField()

    def __str__(self):
        return self.nombre
