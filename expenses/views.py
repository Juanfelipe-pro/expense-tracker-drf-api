from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Expense
from .serializers import ExpenseSerializer, ExpenseListSerializer, ExpenseStatsSerializer
from .permissions import IsOwner
from .filters import ExpenseFilter


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de Expense.
    
    Endpoints generados automáticamente:
    - GET    /api/expenses/           → list()    (listar)
    - POST   /api/expenses/           → create()  (crear)
    - GET    /api/expenses/{id}/      → retrieve() (ver detalle)
    - PUT    /api/expenses/{id}/      → update()  (actualizar completo)
    - PATCH  /api/expenses/{id}/      → partial_update() (actualizar parcial)
    - DELETE /api/expenses/{id}/      → destroy() (eliminar)
    """
    
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    # Configuración de filtros
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ExpenseFilter
    search_fields = ['title', 'description']  # Búsqueda en estos campos
    ordering_fields = ['date', 'amount', 'created_at']  # Ordenamiento permitido
    ordering = ['-date']  # Ordenamiento por defecto
    
    def get_queryset(self):
        """
        Sobrescribe el queryset para filtrar solo gastos del usuario autenticado.
        
        Esto asegura que cada usuario solo vea sus propios gastos.
        
        Returns:
            QuerySet: Gastos del usuario autenticado
        """
        # Solo retornar gastos del usuario autenticado
        return Expense.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Retorna diferentes serializers según la acción.
        
        Returns:
            Serializer: La clase de serializer apropiada
        """
        if self.action == 'list':
            # Para listar, usar serializer simplificado
            return ExpenseListSerializer
        return ExpenseSerializer
    
    def perform_create(self, serializer):
        """
        Sobrescribe la creación para asignar automáticamente el usuario.
        
        Args:
            serializer: El serializer validado
        """
        # Guardar asignando el usuario autenticado
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint personalizado para obtener estadísticas.
        
        GET /api/expenses/stats/
        
        Returns:
            Response: Estadísticas de gastos del usuario
        """
        # Obtener gastos del usuario
        expenses = self.get_queryset()
        
        # Calcular estadísticas
        stats = expenses.aggregate(
            total_expenses=Count('id'),
            total_amount=Sum('amount'),
            average_amount=Avg('amount')
        )
        
        # Manejar valores None cuando no hay gastos
        if stats['total_amount'] is None:
            stats['total_amount'] = 0
        if stats['average_amount'] is None:
            stats['average_amount'] = 0
        
        # Gastos por categoría
        by_category = {}
        for choice in Expense.CATEGORY_CHOICES:
            category_code = choice[0]
            category_name = choice[1]
            
            category_total = expenses.filter(
                category=category_code
            ).aggregate(total=Sum('amount'))
            
            by_category[category_name] = category_total['total'] or 0
        
        # Agregar breakdown por categoría
        stats['by_category'] = by_category
        
        # Serializar
        serializer = ExpenseStatsSerializer(stats)
        
        return Response(serializer.data)