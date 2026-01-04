from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Manager personalizado para el modelo CustomUser.
    
    Define cómo crear usuarios y superusuarios usando email
    en lugar de username.
    """
    
    def create_user(self, email, password, **extra_fields):
        """
        Crea y guarda un usuario regular con email y password.
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña
            **extra_fields: Campos adicionales (first_name, last_name, etc.)
        
        Returns:
            CustomUser: Instancia del usuario creado
        
        Raises:
            ValueError: Si no se proporciona email
        """
        if not email:
            raise ValueError(_('El email es obligatorio'))
        
        # Normalizar email (convertir dominio a minúsculas)
        # ejemplo@GMAIL.com -> ejemplo@gmail.com
        email = self.normalize_email(email)
        
        # Crear instancia del usuario (aún no guardada en BD)
        user = self.model(email=email, **extra_fields)
        
        # Establecer password encriptado
        user.set_password(password)
        
        # Guardar en base de datos
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        """
        Crea y guarda un superusuario con privilegios de admin.
        
        Args:
            email (str): Email del superusuario
            password (str): Contraseña
            **extra_fields: Campos adicionales
        
        Returns:
            CustomUser: Instancia del superusuario creado
        """
        # Establecer valores por defecto para superusuario
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        # Validar que los campos estén correctos
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('El superusuario debe tener is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('El superusuario debe tener is_superuser=True'))
        
        # Usar el método create_user para crear el superusuario
        return self.create_user(email, password, **extra_fields)