from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("El usuario debe tener un email")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)  # Usamos 'username' aquí
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)  # Usamos 'username' aquí
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)

    # Agregar relaciones con groups y user_permissions
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',  # Cambiar el related_name para evitar conflictos
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # Cambiar el related_name para evitar conflictos
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'  # Este es el campo que se usará para login
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email
