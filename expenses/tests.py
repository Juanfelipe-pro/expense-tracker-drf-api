from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import date, timedelta

from .models import Expense

User = get_user_model()


class ExpenseModelTest(TestCase):
    """Tests para el modelo Expense"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            email='expense@example.com',
            password='Password123!',
            first_name='Expense',
            last_name='User'
        )
    
    def test_create_expense(self):
        """Test: Crear un gasto"""
        expense = Expense.objects.create(
            user=self.user,
            title='Supermercado',
            amount=Decimal('50000.00'),
            category='GROCERIES',
            description='Compra del mes',
            date=date.today()
        )
        
        self.assertEqual(expense.title, 'Supermercado')
        self.assertEqual(expense.amount, Decimal('50000.00'))
        self.assertEqual(expense.category, 'GROCERIES')
        self.assertEqual(expense.user, self.user)
        self.assertIsNotNone(expense.created_at)
        self.assertIsNotNone(expense.updated_at)
    
    def test_expense_str_representation(self):
        """Test: Representación en string del gasto"""
        expense = Expense.objects.create(
            user=self.user,
            title='Test Expense',
            amount=Decimal('10000.00'),
            category='LEISURE',
            date=date(2024, 1, 15)
        )
        
        expected = f"Test Expense - $10000.00 (2024-01-15)"
        self.assertEqual(str(expense), expected)
    
    def test_expense_get_category_display(self):
        """Test: Obtener nombre legible de categoría"""
        expense = Expense.objects.create(
            user=self.user,
            title='Test',
            amount=Decimal('10000.00'),
            category='GROCERIES',
            date=date.today()
        )
        
        self.assertEqual(expense.get_category_display(), 'Comestibles')
    
    def test_expense_ordering(self):
        """Test: Ordenamiento de gastos (más recientes primero)"""
        expense1 = Expense.objects.create(
            user=self.user,
            title='Gasto antiguo',
            amount=Decimal('10000.00'),
            category='GROCERIES',
            date=date.today() - timedelta(days=5)
        )
        
        expense2 = Expense.objects.create(
            user=self.user,
            title='Gasto reciente',
            amount=Decimal('20000.00'),
            category='LEISURE',
            date=date.today()
        )
        
        expenses = list(Expense.objects.all())
        self.assertEqual(expenses[0], expense2)  # Más reciente primero
        self.assertEqual(expenses[1], expense1)
    
    def test_expense_cascade_delete(self):
        """Test: Eliminar usuario elimina sus gastos"""
        expense = Expense.objects.create(
            user=self.user,
            title='Test',
            amount=Decimal('10000.00'),
            category='GROCERIES',
            date=date.today()
        )
        
        expense_id = expense.id
        self.user.delete()
        
        self.assertFalse(Expense.objects.filter(id=expense_id).exists())


class ExpenseViewSetTest(TestCase):
    """Tests para el ViewSet de Expense"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='Password123!',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='Password123!',
            first_name='User',
            last_name='Two'
        )
        
        # Crear gastos para user1
        self.expense1 = Expense.objects.create(
            user=self.user1,
            title='Gasto 1',
            amount=Decimal('10000.00'),
            category='GROCERIES',
            date=date.today()
        )
        self.expense2 = Expense.objects.create(
            user=self.user1,
            title='Gasto 2',
            amount=Decimal('20000.00'),
            category='LEISURE',
            date=date.today() - timedelta(days=1)
        )
        
        # Crear gasto para user2
        self.expense3 = Expense.objects.create(
            user=self.user2,
            title='Gasto User 2',
            amount=Decimal('30000.00'),
            category='ELECTRONICS',
            date=date.today()
        )
    
    def get_auth_headers(self, user):
        """Helper para obtener headers de autenticación"""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_expenses_authenticated(self):
        """Test: Listar gastos autenticado"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Solo gastos de user1
        
        # Verificar que solo ve sus propios gastos
        expense_ids = [exp['id'] for exp in response.data['results']]
        self.assertIn(self.expense1.id, expense_ids)
        self.assertIn(self.expense2.id, expense_ids)
        self.assertNotIn(self.expense3.id, expense_ids)
    
    def test_list_expenses_unauthenticated(self):
        """Test: Listar gastos sin autenticación"""
        url = reverse('expenses:expense-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_expense_success(self):
        """Test: Crear gasto exitoso"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-list')
        
        data = {
            'title': 'Nuevo Gasto',
            'amount': '50000.00',
            'category': 'UTILITIES',
            'description': 'Pago de servicios',
            'date': str(date.today())
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Nuevo Gasto')
        self.assertEqual(response.data['amount'], '50000.00')
        
        # Verificar que se asignó el usuario correcto
        expense = Expense.objects.get(id=response.data['id'])
        self.assertEqual(expense.user, self.user1)
    
    def test_create_expense_with_future_date(self):
        """Test: Crear gasto con fecha futura debe fallar"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-list')
        
        data = {
            'title': 'Gasto Futuro',
            'amount': '10000.00',
            'category': 'GROCERIES',
            'date': str(date.today() + timedelta(days=1))
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_expense_with_negative_amount(self):
        """Test: Crear gasto con monto negativo debe fallar"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-list')
        
        data = {
            'title': 'Gasto Negativo',
            'amount': '-1000.00',
            'category': 'GROCERIES',
            'date': str(date.today())
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_expense_large_amount_without_description(self):
        """Test: Crear gasto grande sin descripción debe fallar"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-list')
        
        data = {
            'title': 'Gasto Grande',
            'amount': '2000000.00',  # Mayor a 1,000,000
            'category': 'ELECTRONICS',
            'date': str(date.today())
            # Sin descripción
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)
    
    def test_retrieve_expense_owner(self):
        """Test: Ver detalle de gasto propio"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-detail', kwargs={'pk': self.expense1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.expense1.id)
        self.assertEqual(response.data['title'], 'Gasto 1')
    
    def test_retrieve_expense_other_user(self):
        """Test: Intentar ver gasto de otro usuario debe fallar"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-detail', kwargs={'pk': self.expense3.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_expense_owner(self):
        """Test: Actualizar gasto propio"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-detail', kwargs={'pk': self.expense1.id})
        
        data = {
            'title': 'Gasto Actualizado',
            'amount': '15000.00',
            'category': 'GROCERIES',
            'date': str(date.today())
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.expense1.refresh_from_db()
        self.assertEqual(self.expense1.title, 'Gasto Actualizado')
        self.assertEqual(self.expense1.amount, Decimal('15000.00'))
    
    def test_update_expense_other_user(self):
        """Test: Intentar actualizar gasto de otro usuario debe fallar"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-detail', kwargs={'pk': self.expense3.id})
        
        data = {'title': 'Intento de hack'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_expense_owner(self):
        """Test: Eliminar gasto propio"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-detail', kwargs={'pk': self.expense1.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Expense.objects.filter(id=self.expense1.id).exists())
    
    def test_delete_expense_other_user(self):
        """Test: Intentar eliminar gasto de otro usuario debe fallar"""
        self.client.credentials(**self.get_auth_headers(self.user1))
        url = reverse('expenses:expense-detail', kwargs={'pk': self.expense3.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verificar que el gasto sigue existiendo
        self.assertTrue(Expense.objects.filter(id=self.expense3.id).exists())


class ExpenseFilterTest(TestCase):
    """Tests para los filtros de Expense"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='filter@example.com',
            password='Password123!',
            first_name='Filter',
            last_name='User'
        )
        
        # Crear gastos de prueba
        today = date.today()
        self.expense1 = Expense.objects.create(
            user=self.user,
            title='Gasto Comestibles',
            amount=Decimal('10000.00'),
            category='GROCERIES',
            date=today
        )
        self.expense2 = Expense.objects.create(
            user=self.user,
            title='Gasto Entretenimiento',
            amount=Decimal('50000.00'),
            category='LEISURE',
            date=today - timedelta(days=5)
        )
        self.expense3 = Expense.objects.create(
            user=self.user,
            title='Gasto Electrónicos',
            amount=Decimal('200000.00'),
            category='ELECTRONICS',
            date=today - timedelta(days=10)
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_filter_by_category(self):
        """Test: Filtrar por categoría"""
        url = reverse('expenses:expense-list')
        response = self.client.get(url, {'category': 'GROCERIES'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category'], 'GROCERIES')
    
    def test_filter_by_date_range(self):
        """Test: Filtrar por rango de fechas"""
        url = reverse('expenses:expense-list')
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        
        response = self.client.get(url, {
            'start_date': str(start_date),
            'end_date': str(end_date)
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe incluir expense1 y expense2, pero no expense3
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_filter_by_amount_range(self):
        """Test: Filtrar por rango de montos"""
        url = reverse('expenses:expense-list')
        
        response = self.client.get(url, {
            'min_amount': '50000.00',
            'max_amount': '100000.00'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo expense2 debería estar en este rango
        results = response.data['results']
        for expense in results:
            amount = Decimal(expense['amount'])
            self.assertGreaterEqual(amount, Decimal('50000.00'))
            self.assertLessEqual(amount, Decimal('100000.00'))
    
    def test_filter_by_period_week(self):
        """Test: Filtrar por período semana"""
        url = reverse('expenses:expense-list')
        
        response = self.client.get(url, {'period': 'week'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe incluir gastos de los últimos 7 días
        results = response.data['results']
        for expense in results:
            expense_date = date.fromisoformat(expense['date'])
            days_ago = (date.today() - expense_date).days
            self.assertLessEqual(days_ago, 7)
    
    def test_search_by_title(self):
        """Test: Búsqueda por título"""
        url = reverse('expenses:expense-list')
        
        response = self.client.get(url, {'search': 'Comestibles'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertIn('Comestibles', response.data['results'][0]['title'])


class ExpenseStatsTest(TestCase):
    """Tests para el endpoint de estadísticas"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='stats@example.com',
            password='Password123!',
            first_name='Stats',
            last_name='User'
        )
        
        # Crear gastos de prueba
        Expense.objects.create(
            user=self.user,
            title='Gasto 1',
            amount=Decimal('10000.00'),
            category='GROCERIES',
            date=date.today()
        )
        Expense.objects.create(
            user=self.user,
            title='Gasto 2',
            amount=Decimal('20000.00'),
            category='GROCERIES',
            date=date.today()
        )
        Expense.objects.create(
            user=self.user,
            title='Gasto 3',
            amount=Decimal('30000.00'),
            category='LEISURE',
            date=date.today()
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_stats_endpoint(self):
        """Test: Obtener estadísticas"""
        url = reverse('expenses:expense-stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_expenses', response.data)
        self.assertIn('total_amount', response.data)
        self.assertIn('average_amount', response.data)
        self.assertIn('by_category', response.data)
        
        self.assertEqual(response.data['total_expenses'], 3)
        self.assertEqual(Decimal(response.data['total_amount']), Decimal('60000.00'))
        self.assertEqual(Decimal(response.data['average_amount']), Decimal('20000.00'))
        
        # Verificar breakdown por categoría
        by_category = response.data['by_category']
        self.assertIn('Comestibles', by_category)
        self.assertIn('Entretenimiento', by_category)
        self.assertEqual(Decimal(str(by_category['Comestibles'])), Decimal('30000.00'))
        self.assertEqual(Decimal(str(by_category['Entretenimiento'])), Decimal('30000.00'))
    
    def test_stats_empty(self):
        """Test: Estadísticas sin gastos"""
        # Crear otro usuario sin gastos
        user2 = User.objects.create_user(
            email='nostats@example.com',
            password='Password123!',
            first_name='No',
            last_name='Stats'
        )
        
        refresh = RefreshToken.for_user(user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('expenses:expense-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_expenses'], 0)
        self.assertEqual(Decimal(response.data['total_amount']), Decimal('0.00'))


class ExpenseSerializerTest(TestCase):
    """Tests para los serializers de Expense"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            email='serializer@example.com',
            password='Password123!',
            first_name='Serializer',
            last_name='User'
        )
    
    def test_expense_serializer_validation(self):
        """Test: Validaciones del serializer"""
        from .serializers import ExpenseSerializer
        
        # Test con monto negativo
        data = {
            'title': 'Test',
            'amount': Decimal('-100.00'),
            'category': 'GROCERIES',
            'date': date.today()
        }
        serializer = ExpenseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        
        # Test con fecha futura
        data = {
            'title': 'Test',
            'amount': Decimal('100.00'),
            'category': 'GROCERIES',
            'date': date.today() + timedelta(days=1)
        }
        serializer = ExpenseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('date', serializer.errors)
        
        # Test con gasto grande sin descripción
        data = {
            'title': 'Test',
            'amount': Decimal('2000000.00'),
            'category': 'ELECTRONICS',
            'date': date.today()
        }
        serializer = ExpenseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

