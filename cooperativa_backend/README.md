# Sistema de Gestión Agrícola Cooperativa - Backend Django

Este es el backend de Django para el sistema de gestión agrícola de la cooperativa, construido con Django REST Framework.

## Características Implementadas

### Modelos de Datos
- **Usuario**: Modelo de usuario personalizado con autenticación
- **Rol**: Sistema de roles con permisos JSON
- **Comunidad**: Gestión de comunidades
- **Socio**: Información extendida de los socios
- **Parcela**: Gestión de parcelas agrícolas
- **Cultivo**: Seguimiento de cultivos por parcela
- **BitacoraAuditoria**: Sistema de auditoría completo
- **CicloCultivo**: Gestión avanzada de ciclos de cultivo (CU4)
- **Cosecha**: Registro detallado de cosechas (CU4)
- **Tratamiento**: Seguimiento de tratamientos aplicados (CU4)
- **AnalisisSuelo**: Análisis de suelo con recomendaciones (CU4)
- **TransferenciaParcela**: Transferencias de propiedad de parcelas (CU4)

### API REST
- Endpoints completos para CRUD en todos los modelos
- Autenticación de usuarios
- Sistema de permisos basado en roles
- Paginación automática
- Filtros y búsqueda

### Seguridad
- Autenticación personalizada
- Control de intentos de login fallidos
- Sistema de bloqueo de cuentas
- Auditoría completa de todas las operaciones

### Gestión Avanzada de Parcelas y Cultivos (CU4)
- **Ciclos de Cultivo**: Planificación y seguimiento de ciclos agrícolas
- **Cosechas**: Registro detallado con cálculos automáticos de valor
- **Tratamientos**: Seguimiento de fertilizantes, pesticidas y tratamientos
- **Análisis de Suelo**: Análisis con recomendaciones automáticas basadas en pH y nutrientes
- **Transferencias de Parcelas**: Sistema completo de transferencias con validaciones
- **Reportes de Productividad**: Estadísticas avanzadas de rendimiento por parcela y especie

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Django 5.0
- PostgreSQL (recomendado) o SQLite

### Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar la base de datos:**
   - Para PostgreSQL, actualiza `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'cooperativa',
           'USER': 'tu_usuario',
           'PASSWORD': 'tu_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **Ejecutar migraciones:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Crear superusuario:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Ejecutar el servidor:**
   ```bash
   python manage.py runserver localhost:8000
   ```

## API Endpoints

### Autenticación
- `POST /api/usuarios/login/` - Login de usuario
- `POST /api/usuarios/{id}/cambiar_password/` - Cambiar contraseña

### Gestión de Usuarios
- `GET /api/usuarios/` - Listar usuarios
- `POST /api/usuarios/` - Crear usuario
- `GET /api/usuarios/{id}/` - Detalle de usuario
- `PUT /api/usuarios/{id}/` - Actualizar usuario
- `DELETE /api/usuarios/{id}/` - Eliminar usuario

### Gestión de Roles
- `GET /api/roles/` - Listar roles
- `POST /api/roles/` - Crear rol
- `GET /api/roles/{id}/` - Detalle de rol
- `PUT /api/roles/{id}/` - Actualizar rol
- `DELETE /api/roles/{id}/` - Eliminar rol

### Gestión de Comunidades
- `GET /api/comunidades/` - Listar comunidades
- `POST /api/comunidades/` - Crear comunidad
- `GET /api/comunidades/{id}/` - Detalle de comunidad
- `PUT /api/comunidades/{id}/` - Actualizar comunidad
- `DELETE /api/comunidades/{id}/` - Eliminar comunidad

### Gestión de Socios
- `GET /api/socios/` - Listar socios
- `POST /api/socios/` - Crear socio
- `GET /api/socios/{id}/` - Detalle de socio
- `PUT /api/socios/{id}/` - Actualizar socio
- `DELETE /api/socios/{id}/` - Eliminar socio

### Gestión de Parcelas
- `GET /api/parcelas/` - Listar parcelas
- `POST /api/parcelas/` - Crear parcela
- `GET /api/parcelas/{id}/` - Detalle de parcela
- `PUT /api/parcelas/{id}/` - Actualizar parcela
- `DELETE /api/parcelas/{id}/` - Eliminar parcela

### Gestión de Cultivos
- `GET /api/cultivos/` - Listar cultivos
- `POST /api/cultivos/` - Crear cultivo
- `GET /api/cultivos/{id}/` - Detalle de cultivo
- `PUT /api/cultivos/{id}/` - Actualizar cultivo
- `DELETE /api/cultivos/{id}/` - Eliminar cultivo

### Gestión Avanzada de Parcelas y Cultivos (CU4)
#### Ciclos de Cultivo
- `GET /api/ciclo-cultivos/` - Listar ciclos de cultivo
- `POST /api/ciclo-cultivos/` - Crear ciclo de cultivo
- `GET /api/ciclo-cultivos/{id}/` - Detalle de ciclo
- `PUT /api/ciclo-cultivos/{id}/` - Actualizar ciclo
- `DELETE /api/ciclo-cultivos/{id}/` - Eliminar ciclo

#### Cosechas
- `GET /api/cosechas/` - Listar cosechas
- `POST /api/cosechas/` - Registrar cosecha
- `GET /api/cosechas/{id}/` - Detalle de cosecha
- `PUT /api/cosechas/{id}/` - Actualizar cosecha
- `DELETE /api/cosechas/{id}/` - Eliminar cosecha

#### Tratamientos
- `GET /api/tratamientos/` - Listar tratamientos
- `POST /api/tratamientos/` - Registrar tratamiento
- `GET /api/tratamientos/{id}/` - Detalle de tratamiento
- `PUT /api/tratamientos/{id}/` - Actualizar tratamiento
- `DELETE /api/tratamientos/{id}/` - Eliminar tratamiento

#### Análisis de Suelo
- `GET /api/analisis-suelo/` - Listar análisis
- `POST /api/analisis-suelo/` - Crear análisis
- `GET /api/analisis-suelo/{id}/` - Detalle de análisis
- `PUT /api/analisis-suelo/{id}/` - Actualizar análisis
- `DELETE /api/analisis-suelo/{id}/` - Eliminar análisis

#### Transferencias de Parcelas
- `GET /api/transferencias-parcela/` - Listar transferencias
- `POST /api/transferencias-parcela/` - Crear transferencia
- `GET /api/transferencias-parcela/{id}/` - Detalle de transferencia
- `PUT /api/transferencias-parcela/{id}/` - Actualizar transferencia
- `DELETE /api/transferencias-parcela/{id}/` - Eliminar transferencia
- `POST /api/transferencias-parcela/{id}/procesar/` - Procesar transferencia

#### Reportes y Búsquedas Avanzadas
- `GET /api/buscar/ciclos-cultivo/` - Búsqueda avanzada de ciclos
- `GET /api/reportes/productividad-parcelas/` - Reporte de productividad
- `GET /api/validar/transferencia-parcela/` - Validar transferencia

### Auditoría
- `GET /api/bitacora/` - Ver registros de auditoría

## Modelo de Datos

### Usuario
```json
{
  "id": 1,
  "ci_nit": "1234567",
  "nombres": "Juan",
  "apellidos": "Pérez",
  "email": "juan@example.com",
  "telefono": "77712345",
  "usuario": "jperez",
  "estado": "ACTIVO",
  "roles": ["Administrador"]
}
```

### Parcela
```json
{
  "id": 1,
  "socio": 1,
  "socio_nombre": "Juan Pérez",
  "nombre": "Parcela Norte",
  "superficie_hectareas": 5.5,
  "tipo_suelo": "Arcilloso",
  "ubicacion": "Zona norte de la comunidad",
  "coordenadas": "-63.123,-17.456",
  "estado": "ACTIVA"
}
```

### Cultivo
```json
{
  "id": 1,
  "parcela": 1,
  "parcela_nombre": "Parcela Norte",
  "socio_nombre": "Juan Pérez",
  "especie": "Maíz",
  "variedad": "Amarillo",
  "tipo_semilla": "Híbrida",
  "fecha_estimada_siembra": "2024-10-15",
  "hectareas_sembradas": 3.0,
  "estado": "ACTIVO"
}
```

## Próximos Pasos

### ✅ Completado
1. **CU1**: Autenticación y gestión de sesiones ✅
2. **CU2**: Gestión de logout y sesiones avanzadas ✅
3. **CU3**: Gestión avanzada de socios, usuarios y roles ✅
4. **CU4**: Gestión avanzada de parcelas y cultivos ✅

### Pendientes
1. **Implementar triggers de auditoría en la base de datos**
2. **Agregar PostGIS para coordenadas geográficas**
3. **Implementar notificaciones y alertas**
4. **Agregar reportes y estadísticas adicionales**
5. **Implementar API de archivos para subir documentos**
6. **Agregar sistema de backup y recuperación**

## Desarrollo

Para contribuir al desarrollo:

1. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
2. Realiza tus cambios
3. Ejecuta las pruebas: `python manage.py test`
4. Crea una solicitud de pull

## Licencia

Este proyecto está bajo la Licencia MIT.