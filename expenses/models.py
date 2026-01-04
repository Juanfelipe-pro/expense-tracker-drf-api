from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Expense(models.Model):
    """
    Modelo para registrar gastos de usuarios.
    
    Cada usuario puede tener múltiples gastos.
    Cada gasto pertenece a una categoría específica.
    """
    
    # Categorías disponibles
    CATEGORY_CHOICES = [
        ('GROCERIES', 'Comestibles'),
        ('LEISURE', 'Entretenimiento'),
        ('ELECTRONICS', 'Electrónicos'),
        ('UTILITIES', 'Servicios Públicos'),
        ('CLOTHING', 'Ropa'),
        ('HEALTH', 'Salud'),
        ('OTHERS', 'Otros'),
    ]
    
    # Relación con el usuario
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Usa el modelo de usuario personalizado
        on_delete=models.CASCADE,  # Si se elimina el usuario, se eliminan sus gastos
        related_name='expenses',   # user.expenses.all()
        verbose_name=_('usuario')
    )
    
    # Información del gasto
    title = models.CharField(
        _('título'),
        max_length=200,
        help_text=_('Breve descripción del gasto')
    )
    
    amount = models.DecimalField(
        _('monto'),
        max_digits=10,           # Máximo 10 dígitos en total
        decimal_places=2,        # 2 decimales (99999999.99)
        validators=[MinValueValidator(0.01)],  # Mínimo 0.01
        help_text=_('Monto del gasto en pesos')
    )
    
    category = models.CharField(
        _('categoría'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text=_('Categoría del gasto')
    )
    
    description = models.TextField(
        _('descripción'),
        blank=True,              # Puede estar vacío
        null=True,               # Puede ser NULL en BD
        help_text=_('Descripción detallada del gasto (opcional)')
    )
    
    date = models.DateField(
        _('fecha del gasto'),
        help_text=_('Fecha en que se realizó el gasto')
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(
        _('fecha de creación'),
        auto_now_add=True  # Se establece al crear
    )
    
    updated_at = models.DateTimeField(
        _('última actualización'),
        auto_now=True      # Se actualiza en cada save()
    )
    
    class Meta:
        db_table = 'expenses'
        verbose_name = _('gasto')
        verbose_name_plural = _('gastos')
        ordering = ['-date', '-created_at']  # Más recientes primero
        
        # Índices para búsquedas rápidas
        indexes = [
            models.Index(fields=['user', 'date']),      # Búsquedas por usuario y fecha
            models.Index(fields=['category']),          # Búsquedas por categoría
            models.Index(fields=['date']),              # Búsquedas por fecha
            models.Index(fields=['-date']),             # Ordenamiento descendente
        ]
    
    def __str__(self):
        """
        Representación en string del gasto.
        Ejemplo: "Supermercado - $50000.00 (2024-01-15)"
        """
        return f"{self.title} - ${self.amount} ({self.date})"
    
    def get_category_display_custom(self):
        """
        Método personalizado para mostrar la categoría.
        Django ya tiene get_category_display(), este es solo de ejemplo.
        """
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)