# Sistema de Gestión Cooperativa

Backend Django REST API para la gestión completa de una cooperativa agrícola, incluyendo autenticación, gestión de usuarios, socios, parcelas y cultivos.

## Características Implementadas

### ✅ Caso de Estudio - Tareas Completadas
- **CU1**: Iniciar sesión (web/móvil) con validación y bloqueo de cuenta
- **T011**: Autenticación y gestión de sesiones
- **T013**: Bitácora de auditoría básica
- **T020**: Interfaz de login
- **T023**: Cierre de sesión
- **T026**: Vista móvil para consulta de socios

### 🔧 Tecnologías Utilizadas
- **Django 5.0** - Framework web principal
- **Django REST Framework** - API REST
- **PostgreSQL** - Base de datos
- **psycopg2** - Driver PostgreSQL
- **django-cors-headers** - Soporte CORS

## Instalación y Configuración

### 1. Prerrequisitos
- Python 3.8+
- PostgreSQL 12+
- Git

### 2. Clonar el Repositorio
```bash
cd Backend_Django
```

### 3. Crear Entorno Virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Base de Datos PostgreSQL
```sql
-- Crear base de datos
CREATE DATABASE cooperativa_db;

-- Crear usuario
CREATE USER cooperativa_user WITH PASSWORD '123456';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE cooperativa_db TO cooperativa_user;
```

### 6. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
DATABASE_URL=postgresql://cooperativa_user:123456@localhost:5432/cooperativa_db
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
```

### 7. Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 9. Ejecutar Servidor
```bash
python manage.py runserver
```

El servidor estará disponible en: http://localhost:8000

## Uso de la API

### Endpoints Principales

#### Autenticación
- **POST** `/api/auth/login/` - Iniciar sesión
- **POST** `/api/auth/logout/` - Cerrar sesión
- **GET** `/api/auth/status/` - Estado de sesión

#### Datos
- **GET/POST** `/api/socios/` - Gestionar socios
- **GET/POST** `/api/parcelas/` - Gestionar parcelas
- **GET/POST** `/api/cultivos/` - Gestionar cultivos
- **GET** `/api/bitacora/` - Ver bitácora de auditoría

### Ejemplo de Uso con cURL

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### Obtener Socios (requiere token)
```bash
curl -X GET http://localhost:8000/api/socios/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Interfaces Web

### Interfaz de Login
- **URL**: http://localhost:8000/login/
- **Descripción**: Formulario de inicio de sesión con validación JavaScript

### Dashboard
- **URL**: http://localhost:8000/dashboard/
- **Descripción**: Panel principal con estadísticas y menú de navegación

### Vista Móvil de Socios
- **URL**: http://localhost:8000/mobile/socios/
- **Descripción**: Interfaz optimizada para móviles para consultar socios

## Estructura del Proyecto

```
Backend_Django/
├── cooperativa_backend/
│   ├── settings.py          # Configuración de Django
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # Configuración WSGI
├── cooperativa/
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Vistas API y web
│   ├── serializers.py      # Serializers REST
│   ├── urls.py             # URLs de la app
│   └── templates/          # Plantillas HTML
│       ├── auth/
│       │   └── login.html
│       ├── dashboard.html
│       └── mobile/
│           └── socios.html
├── docs/
│   └── API_Documentation.md # Documentación completa
├── test/
│   ├── Test_Cases.md       # Casos de prueba
│   └── test_models.py      # Pruebas unitarias
└── manage.py
```

## Seguridad

### Características de Seguridad Implementadas
- ✅ Autenticación basada en sesiones
- ✅ Validación de credenciales
- ✅ Bloqueo de cuenta por intentos fallidos (5 intentos)
- ✅ Bitácora de auditoría completa
- ✅ Filtros de permisos por usuario
- ✅ Validación de datos en modelos
- ✅ Protección CSRF en formularios web

### Políticas de Contraseña
- Longitud mínima: 8 caracteres
- Debe contener letras y números
- No puede ser similar al nombre de usuario

## Testing

### Ejecutar Pruebas
```bash
python manage.py test
```

### Ejecutar Pruebas Específicas
```bash
python manage.py test test.test_models
```

## Documentación Adicional

- 📋 **[Casos de Prueba](docs/Test_Cases.md)** - Casos de prueba detallados
- 📖 **[Documentación API](docs/API_Documentation.md)** - Documentación completa de endpoints
- 🔧 **[Configuración](docs/Setup.md)** - Guía de configuración avanzada

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Soporte

Para soporte técnico o preguntas:
- 📧 Email: soporte@cooperativa.com
- 📱 Teléfono: +591 2 1234567
- 🏢 Dirección: Calle Cooperativa #123, Ciudad

---

**Desarrollado por:** Equipo de Desarrollo Cooperativa
**Versión:** 1.0.0
**Fecha:** Diciembre 2024