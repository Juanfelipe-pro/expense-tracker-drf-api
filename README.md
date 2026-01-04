# 💰 Expense Tracker API

API REST para gestión de gastos personales con autenticación JWT.

## 🚀 Características

- ✅ Autenticación con JWT (JSON Web Tokens)
- ✅ CRUD completo de gastos
- ✅ Filtros por categoría, fecha y monto
- ✅ Estadísticas de gastos por usuario
- ✅ Panel de administración personalizado
- ✅ Documentación interactiva con Swagger
- ✅ Tests automatizados
- ✅ Throttling (límite de peticiones)
- ✅ Logging de errores

## 🛠️ Tecnologías

- Python 3.12+
- Django 5.1
- Django REST Framework
- PostgreSQL
- JWT Authentication
- drf-spectacular (Swagger)

## 📋 Requisitos

- Python 3.12 o superior
- PostgreSQL 14 o superior
- pip

## ⚙️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/expense-tracker-api.git
cd expense-tracker-api
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz:
```env
# Django
SECRET_KEY=tu-secret-key-super-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=expense_tracker_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### 5. Crear base de datos
```bash
psql -U postgres
CREATE DATABASE expense_tracker_db;
\q
```

### 6. Aplicar migraciones
```bash
python manage.py migrate
```

### 7. Crear superusuario
```bash
python manage.py createsuperuser
```

### 8. Iniciar servidor
```bash
python manage.py runserver
```

## 📚 Documentación de la API

Una vez que el servidor esté corriendo, visita:

- **Swagger UI:** http://127.0.0.1:8000/api/docs/
- **ReDoc:** http://127.0.0.1:8000/api/redoc/
- **Admin:** http://127.0.0.1:8000/admin/

## 🔐 Endpoints Principales

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Registrar nuevo usuario |
| POST | `/api/auth/login/` | Iniciar sesión |
| POST | `/api/auth/token/refresh/` | Refrescar token |
| POST | `/api/auth/logout/` | Cerrar sesión |
| GET | `/api/auth/me/` | Obtener perfil del usuario |

### Gastos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/expenses/` | Listar gastos del usuario |
| POST | `/api/expenses/` | Crear nuevo gasto |
| GET | `/api/expenses/{id}/` | Ver detalle de gasto |
| PUT | `/api/expenses/{id}/` | Actualizar gasto completo |
| PATCH | `/api/expenses/{id}/` | Actualizar gasto parcial |
| DELETE | `/api/expenses/{id}/` | Eliminar gasto |
| GET | `/api/expenses/stats/` | Estadísticas de gastos |

### Filtros Disponibles
```
?category=GROCERIES          # Por categoría
?period=week                 # Última semana
?period=month                # Último mes
?period=3months              # Últimos 3 meses
?start_date=2024-01-01       # Fecha inicio
?end_date=2024-12-31         # Fecha fin
?min_amount=10000            # Monto mínimo
?max_amount=100000           # Monto máximo
?search=netflix              # Búsqueda en título/descripción
?ordering=-amount            # Ordenar por monto descendente
```

## 🧪 Ejecutar Tests
```bash
python manage.py test
```

## 📊 Categorías de Gastos

- `GROCERIES` - Comestibles
- `LEISURE` - Entretenimiento
- `ELECTRONICS` - Electrónicos
- `UTILITIES` - Servicios Públicos
- `CLOTHING` - Ropa
- `HEALTH` - Salud
- `OTHERS` - Otros

## 🔒 Seguridad

- Autenticación JWT con tokens de corta duración
- Throttling (límite de peticiones)
- Validación de contraseñas robustas
- Protección CSRF
- Headers de seguridad HTTP
- HTTPS en producción

## 📝 Licencia

MIT

## 👤 Autor
**Juan Felipe Alvear Estrada**
* [GitHub](https://github.com/Juanfelipe-pro)
* [Email](mailto:juanfelipealvearestrada@gmail.com)