from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar información del usuario.
    
    Se usa para respuestas GET (mostrar datos del usuario).
    No incluye el password por seguridad.
    """
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'date_joined', 'is_active')
        read_only_fields = ('id', 'date_joined')
    
    def get_full_name(self, obj):
        """
        Método personalizado para obtener el nombre completo.
        
        Args:
            obj: Instancia del usuario
            
        Returns:
            str: Nombre completo del usuario
        """
        return obj.get_full_name()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios.
    
    Valida:
        - Email único
        - Contraseña segura
        - Confirmación de contraseña
    """
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Este correo electrónico ya está registrado."
        )]
    )
    
    password = serializers.CharField(
        write_only=True,  # No se devuelve en respuestas
        required=True,
        validators=[validate_password],  # Valida que sea segura
        style={'input_type': 'password'}
    )
    
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirmar contraseña"
    )
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate(self, attrs):
        """
        Validación a nivel de objeto.
        
        Verifica que las contraseñas coincidan.
        
        Args:
            attrs (dict): Datos validados
            
        Returns:
            dict: Datos validados
            
        Raises:
            ValidationError: Si las contraseñas no coinciden
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Crea un nuevo usuario.
        
        Args:
            validated_data (dict): Datos validados del formulario
            
        Returns:
            User: Usuario creado
        """
        # Remover password2 (solo era para validación)
        validated_data.pop('password2')
        
        # Crear usuario usando el manager
        user = User.objects.create_user(**validated_data)
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer para validar datos de login.
    
    No está ligado a ningún modelo (Serializer, no ModelSerializer).
    Solo valida que el email y password estén presentes.
    """
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar contraseña.
    
    Requiere la contraseña actual y la nueva.
    """
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Valida que las nuevas contraseñas coincidan."""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Las contraseñas no coinciden."
            })
        return attrs