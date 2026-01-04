from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los dueños editar un objeto.
    
    Los usuarios solo pueden ver y editar sus propios gastos.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica si el usuario tiene permiso sobre este objeto específico.
        
        Args:
            request: El objeto request
            view: La vista que está manejando la petición
            obj: El objeto Expense que se está accediendo
            
        Returns:
            bool: True si tiene permiso, False si no
        """
        # Permitir cualquier método si el usuario es el dueño
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos, pero escritura solo al dueño.
    
    (No lo usaremos, pero es un ejemplo útil)
    """
    
    def has_object_permission(self, request, view, obj):
        # Métodos de lectura (GET, HEAD, OPTIONS) permitidos para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Métodos de escritura (POST, PUT, PATCH, DELETE) solo para el dueño
        return obj.user == request.user