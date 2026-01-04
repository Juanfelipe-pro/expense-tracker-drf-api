from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Admin simple para CustomUser.
    """
    
    # Columnas que se muestran en la lista
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'date_joined',
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    ]
    
    # Campos donde se puede buscar
    search_fields = [
        'email',
        'first_name',
        'last_name',
    ]
    
    # Ordenamiento por defecto
    ordering = ['-date_joined']
    
    # Organización del formulario de edición
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Información Personal'), {
            'fields': ('first_name', 'last_name')
        }),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        (_('Fechas'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    # Formulario para crear nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
            ),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['date_joined', 'last_login']