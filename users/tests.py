from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime

User = get_user_model()


class UserModelTest(TestCase):
    """Tests para el modelo CustomUser"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Juan',
            'last_name': 'Pérez'
        }
    
    def test_create_user(self):
        """Test: Crear un usuario normal"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Juan')
        self.assertEqual(user.last_name, 'Pérez')
        self.assertTrue(user.check_password('TestPassword123!'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test: Crear un superusuario"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_str_representation(self):
        """Test: Representación en string del usuario"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')
    
    def test_get_full_name(self):
        """Test: Obtener nombre completo"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'Juan Pérez')
    
    def test_get_short_name(self):
        """Test: Obtener nombre corto"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), 'Juan')
    
    def test_email_normalization(self):
        """Test: Normalización de email"""
        user = User.objects.create_user(
            email='TEST@EXAMPLE.COM',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, 'TEST@example.com')  # Solo dominio se normaliza
    
    def test_user_without_email_raises_error(self):
        """Test: Crear usuario sin email debe fallar"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='TestPassword123!',
                first_name='Test',
                last_name='User'
            )


class RegisterViewTest(TestCase):
    """Tests para el endpoint de registro"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('users:register')
        self.valid_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'first_name': 'Nuevo',
            'last_name': 'Usuario'
        }
    
    def test_register_user_success(self):
        """Test: Registro exitoso de usuario"""
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        
        # Verificar que el usuario fue creado
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_register_with_existing_email(self):
        """Test: Registro con email existente debe fallar"""
        User.objects.create_user(
            email='existing@example.com',
            password='Password123!',
            first_name='Existing',
            last_name='User'
        )
        
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_with_password_mismatch(self):
        """Test: Registro con contraseñas que no coinciden"""
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPassword123!'
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_register_with_weak_password(self):
        """Test: Registro con contraseña débil"""
        data = self.valid_data.copy()
        data['password'] = '123'  # Contraseña muy débil
        data['password2'] = '123'
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_missing_fields(self):
        """Test: Registro con campos faltantes"""
        data = {'email': 'test@example.com'}  # Faltan campos requeridos
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(TestCase):
    """Tests para el endpoint de login"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('users:login')
        self.user = User.objects.create_user(
            email='login@example.com',
            password='LoginPassword123!',
            first_name='Login',
            last_name='User'
        )
    
    def test_login_success(self):
        """Test: Login exitoso"""
        data = {
            'email': 'login@example.com',
            'password': 'LoginPassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)
    
    def test_login_with_wrong_password(self):
        """Test: Login con contraseña incorrecta"""
        data = {
            'email': 'login@example.com',
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_login_with_nonexistent_user(self):
        """Test: Login con usuario inexistente"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_inactive_user(self):
        """Test: Login con usuario inactivo"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'email': 'login@example.com',
            'password': 'LoginPassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)


class LogoutViewTest(TestCase):
    """Tests para el endpoint de logout"""
    
    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse('users:logout')
        self.user = User.objects.create_user(
            email='logout@example.com',
            password='LogoutPassword123!',
            first_name='Logout',
            last_name='User'
        )
    
    def test_logout_success(self):
        """Test: Logout exitoso"""
        # Autenticar usuario
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {'refresh': str(refresh)}
        response = self.client.post(self.logout_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertIn('message', response.data)
    
    def test_logout_without_token(self):
        """Test: Logout sin token de autenticación"""
        response = self.client.post(self.logout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_without_refresh_token(self):
        """Test: Logout sin refresh token en el body"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.post(self.logout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_with_invalid_refresh_token(self):
        """Test: Logout con refresh token inválido"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {'refresh': 'invalid_token'}
        response = self.client.post(self.logout_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileViewTest(TestCase):
    """Tests para el endpoint de perfil de usuario"""
    
    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('users:user-profile')
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='ProfilePassword123!',
            first_name='Profile',
            last_name='User'
        )
    
    def test_get_profile_authenticated(self):
        """Test: Obtener perfil autenticado"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')
        self.assertEqual(response.data['first_name'], 'Profile')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertIn('full_name', response.data)
    
    def test_get_profile_unauthenticated(self):
        """Test: Obtener perfil sin autenticación"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        """Test: Actualizar perfil"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')


class ChangePasswordViewTest(TestCase):
    """Tests para el endpoint de cambio de contraseña"""
    
    def setUp(self):
        self.client = APIClient()
        self.change_password_url = reverse('users:change-password')
        self.user = User.objects.create_user(
            email='changepass@example.com',
            password='OldPassword123!',
            first_name='Change',
            last_name='Password'
        )
    
    def test_change_password_success(self):
        """Test: Cambio de contraseña exitoso"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))
    
    def test_change_password_wrong_old_password(self):
        """Test: Cambio de contraseña con contraseña actual incorrecta"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            'old_password': 'WrongOldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_change_password_mismatch(self):
        """Test: Cambio de contraseña con nuevas contraseñas que no coinciden"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password2': 'DifferentPassword123!'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_unauthenticated(self):
        """Test: Cambio de contraseña sin autenticación"""
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


