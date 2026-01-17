from rest_framework import serializers
from django.utils import timezone
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Expense.
    
    Convierte instancias de Expense a JSON y viceversa.
    Incluye validaciones personalizadas.
    """
    
    # Campos de solo lectura (calculados)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id',
            'user',
            'user_email',          # Email del usuario (read-only)
            'title',
            'amount',
            'category',
            'category_display',    # Nombre legible de categoría (read-only)
            'description',
            'date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        """
        Valida que el monto sea positivo.
        
        Args:
            value: El valor del campo amount
            
        Returns:
            value: El valor validado
            
        Raises:
            ValidationError: Si el monto es <= 0
        """
        if value <= 0:
            raise serializers.ValidationError(
                "El monto debe ser mayor a cero."
            )
        return value
    
    def validate_date(self, value):
        """
        Valida que la fecha no sea futura.
        
        Args:
            value: El valor del campo date
            
        Returns:
            value: El valor validado
            
        Raises:
            ValidationError: Si la fecha es futura
        """
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "La fecha del gasto no puede ser futura."
            )
        return value
    
    def validate(self, attrs):
        """
        Validación a nivel de objeto.
        
        Se ejecuta después de las validaciones de campos individuales.
        
        Args:
            attrs: Diccionario con todos los datos validados
            
        Returns:
            attrs: Datos validados
        """
        # Aquí puedes agregar validaciones que involucren múltiples campos
        # Por ejemplo: validar que gastos grandes tengan descripción
        
        amount = attrs.get('amount')
        description = attrs.get('description')
        
        # Si el gasto es mayor a 1,000,000 y no tiene descripción
        if amount and amount > 1000000 and not description:
            raise serializers.ValidationError({
                'description': 'Los gastos mayores a $1,000,000 requieren descripción.'
            })
        
        return attrs
    
    # El método create() no es necesario aquí porque perform_create() en la vista
    # ya maneja la asignación del usuario. Si se necesita, se puede agregar después.


class ExpenseListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar gastos.
    
    Muestra menos campos para mejor rendimiento en listas.
    """
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id',
            'title',
            'amount',
            'category',
            'category_display',
            'date',
            'created_at'
        ]


class ExpenseStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de gastos.
    
    No está ligado a un modelo (Serializer, no ModelSerializer).
    """
    
    total_expenses = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    by_category = serializers.DictField()