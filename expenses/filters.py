from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import timedelta
from .models import Expense


class ExpenseFilter(filters.FilterSet):
    """
    Filtros personalizados para Expense.
    
    Permite filtrar por:
    - Categoría
    - Rango de fechas
    - Rango de montos
    - Períodos predefinidos (semana, mes, 3 meses)
    """
    
    # Filtro por categoría
    category = filters.ChoiceFilter(
        choices=Expense.CATEGORY_CHOICES,
        help_text="Filtrar por categoría"
    )
    
    # Filtros por rango de fechas
    start_date = filters.DateFilter(
        field_name='date',
        lookup_expr='gte',  # greater than or equal (>=)
        help_text="Fecha de inicio (YYYY-MM-DD)"
    )
    
    end_date = filters.DateFilter(
        field_name='date',
        lookup_expr='lte',  # less than or equal (<=)
        help_text="Fecha de fin (YYYY-MM-DD)"
    )
    
    # Filtros por rango de montos
    min_amount = filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        help_text="Monto mínimo"
    )
    
    max_amount = filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        help_text="Monto máximo"
    )
    
    # Filtro por período predefinido
    period = filters.CharFilter(
        method='filter_by_period',
        help_text="Período: week, month, 3months"
    )
    
    class Meta:
        model = Expense
        fields = ['category', 'start_date', 'end_date', 'min_amount', 'max_amount', 'period']
    
    def filter_by_period(self, queryset, name, value):
        """
        Filtra por períodos predefinidos.
        
        Args:
            queryset: QuerySet de Expense
            name: Nombre del filtro
            value: Valor del período (week, month, 3months)
            
        Returns:
            QuerySet filtrado
        """
        today = timezone.now().date()
        
        if value == 'week':
            # Última semana (7 días)
            start_date = today - timedelta(days=7)
            return queryset.filter(date__gte=start_date)
        
        elif value == 'month':
            # Último mes (30 días)
            start_date = today - timedelta(days=30)
            return queryset.filter(date__gte=start_date)
        
        elif value == '3months':
            # Últimos 3 meses (90 días)
            start_date = today - timedelta(days=90)
            return queryset.filter(date__gte=start_date)
        
        # Si el valor no es válido, retornar sin filtrar
        return queryset