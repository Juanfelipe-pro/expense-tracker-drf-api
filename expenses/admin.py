from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Admin simple para Expense.
    """
    
    # Columnas que se muestran en la lista
    list_display = [
        'id',
        'title',
        'amount',
        'category',
        'user',
        'date',
        'created_at',
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'category',
        'date',
        'user',
    ]
    
    # Campos donde se puede buscar
    search_fields = [
        'title',
        'description',
        'user__email',
    ]
    
    # Ordenamiento por defecto
    ordering = ['-date', '-created_at']
    
    # Campos de solo lectura
    readonly_fields = ['created_at', 'updated_at']
    
    # Paginación
    list_per_page = 25