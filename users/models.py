from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado que usa email en lugar de username.
    
    Hereda de:
        - AbstractBaseUser: Proporciona funcionalidad base de autenticación
        - PermissionsMixin: Agrega campos y métodos para manejo de permisos
    """
    
    # Campos personalizados
    email = models.EmailField(
        _('correo electrónico'),
        unique=True,  # No puede haber dos usuarios con el mismo email
        help_text=_('Correo electrónico único del usuario')
    )
    first_name = models.CharField(
        _('nombre'),
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        _('apellido'),
        max_length=150,
        blank=False
    )
    
    # Campos de control
    is_active = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Indica si el usuario debe ser tratado como activo. '
                    'Desmarca esto en lugar de borrar cuentas.')
    )
    is_staff = models.BooleanField(
        _('staff'),
        default=False,
        help_text=_('Indica si el usuario puede acceder al sitio de administración.')
    )
    
    # Campos de auditoría
    date_joined = models.DateTimeField(
        _('fecha de registro'),
        auto_now_add=True  # Se establece automáticamente al crear
    )
    updated_at = models.DateTimeField(
        _('última actualización'),
        auto_now=True  # Se actualiza automáticamente en cada save()
    )
    
    # Configuración del modelo
    USERNAME_FIELD = 'email'  # Campo usado para login
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Campos requeridos al crear superuser
    
    # Manager personalizado
    objects = CustomUserManager()
    
    class Meta:
        db_table = 'users'  # Nombre de la tabla en PostgreSQL
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['-date_joined']  # Ordenar por más reciente primero
        indexes = [
            models.Index(fields=['email']),  # Índice para búsquedas rápidas
        ]
    
    def __str__(self):
        """
        Representación en string del usuario.
        Se usa en el admin y en shell.
        """
        return self.email
    
    def get_full_name(self):
        """
        Retorna el nombre completo del usuario.
        
        Returns:
            str: Nombre completo (first_name + last_name)
        """
        return f'{self.first_name} {self.last_name}'.strip()
    
    def get_short_name(self):
        """
        Retorna el nombre corto del usuario.
        
        Returns:
            str: Solo el primer nombre
        """
        return self.first_name