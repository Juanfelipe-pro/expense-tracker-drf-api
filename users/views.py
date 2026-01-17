from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Vista para registro de nuevos usuarios.
    
    POST /api/auth/register/
    
    Permite que cualquier persona se registre (AllowAny).
    Devuelve los tokens JWT al registrarse exitosamente.
    """
    
    queryset = User.objects.all()
    permission_classes = (AllowAny,)  # Cualquiera puede registrarse
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescribe el método create para devolver tokens JWT.
        
        Returns:
            Response: Datos del usuario + tokens JWT
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Crear usuario
        user = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Serializar datos del usuario
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Vista para login de usuarios.
    
    POST /api/auth/login/
    
    Valida credenciales y devuelve tokens JWT.
    """
    
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    
    def post(self, request):
        """
        Maneja el login del usuario.
        
        Args:
            request: Objeto request con email y password
            
        Returns:
            Response: Tokens JWT si las credenciales son válidas
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Verificar si el usuario existe primero
        try:
            user = User.objects.get(email=email)
            # Si el usuario existe pero está inactivo
            if not user.is_active:
                return Response({
                    'error': 'Esta cuenta está desactivada.'
                }, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            user = None
        
        # Autenticar usuario
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Generar tokens
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            
            return Response({
                'user': user_serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'message': 'Login exitoso'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Credenciales inválidas.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Vista para logout (invalidar refresh token).
    
    POST /api/auth/logout/
    
    Requiere autenticación.
    """
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        """
        Invalida el refresh token (blacklist).
        
        Args:
            request: Debe incluir 'refresh' token en el body
            
        Returns:
            Response: Mensaje de confirmación
        """
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response({
                    'error': 'Se requiere el refresh token.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Agregar token a la blacklist
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'message': 'Logout exitoso'
            }, status=status.HTTP_205_RESET_CONTENT)
            
        except Exception as e:
            return Response({
                'error': 'Token inválido o expirado.'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vista para ver y actualizar el perfil del usuario autenticado.
    
    GET /api/auth/me/      - Ver perfil
    PUT /api/auth/me/      - Actualizar perfil completo
    PATCH /api/auth/me/    - Actualizar perfil parcial
    
    Requiere autenticación.
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
 
    
    
    def get_object(self):
        """
        Retorna el usuario autenticado actual.
        
        Returns:
            User: Usuario de la petición
        """
        return self.request.user


class ChangePasswordView(APIView):
    """
    Vista para cambiar la contraseña del usuario autenticado.
    
    POST /api/auth/change-password/
    
    Requiere autenticación.
    """
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        """
        Cambia la contraseña del usuario.
        
        Args:
            request: old_password, new_password, new_password2
            
        Returns:
            Response: Mensaje de confirmación
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Verificar contraseña actual
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'error': 'La contraseña actual es incorrecta.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Establecer nueva contraseña
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Contraseña actualizada exitosamente.'
        }, status=status.HTTP_200_OK)