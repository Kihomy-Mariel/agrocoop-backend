# Casos de Prueba - Sistema de Gestión Cooperativa

## Pruebas de Autenticación (CU1, T011, T020, T023)

### Caso de Prueba 1: Login Exitoso
**Descripción:** Verificar que un usuario válido pueda iniciar sesión correctamente.

**Precondiciones:**
- Usuario registrado: admin / admin123
- Servidor ejecutándose

**Pasos:**
1. Acceder a http://localhost:8000/login/
2. Ingresar usuario: "admin"
3. Ingresar contraseña: "admin123"
4. Hacer clic en "Iniciar Sesión"

**Resultado Esperado:**
- Redirección al dashboard
- Mensaje de éxito
- Registro en bitácora de auditoría

### Caso de Prueba 2: Login con Credenciales Inválidas
**Descripción:** Verificar el manejo de credenciales incorrectas.

**Pasos:**
1. Acceder a http://localhost:8000/login/
2. Ingresar usuario: "admin"
3. Ingresar contraseña: "wrongpassword"
4. Hacer clic en "Iniciar Sesión"

**Resultado Esperado:**
- Mensaje de error: "Credenciales inválidas"
- Contador de intentos fallidos incrementado
- Registro en bitácora de auditoría

### Caso de Prueba 3: Bloqueo de Cuenta por Intentos Fallidos
**Descripción:** Verificar que la cuenta se bloquee después de 5 intentos fallidos.

**Pasos:**
1. Intentar login 5 veces con credenciales incorrectas
2. Intentar login con credenciales correctas

**Resultado Esperado:**
- Cuenta bloqueada
- Mensaje: "Cuenta bloqueada. Contacte al administrador"
- Registro en bitácora de auditoría

### Caso de Prueba 4: Cierre de Sesión
**Descripción:** Verificar que el logout funcione correctamente.

**Precondiciones:**
- Usuario autenticado

**Pasos:**
1. Hacer clic en "Cerrar Sesión" desde el dashboard

**Resultado Esperado:**
- Redirección a página de login
- Sesión destruida
- Registro en bitácora de auditoría

## Pruebas de API REST

### Caso de Prueba 5: Obtener Lista de Socios
**Descripción:** Verificar que la API devuelva la lista de socios correctamente.

**Request:**
```
GET /api/socios/
Authorization: Bearer {token}
```

**Resultado Esperado:**
- Status: 200 OK
- Lista de socios en formato JSON
- Solo socios del usuario actual (si no es admin)

### Caso de Prueba 6: Crear Nuevo Socio
**Descripción:** Verificar la creación de un nuevo socio.

**Request:**
```
POST /api/socios/
Authorization: Bearer {token}
Content-Type: application/json

{
    "cedula": "1234567890",
    "usuario": {
        "usuario": "nuevo_socio",
        "password": "password123",
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan@email.com"
    },
    "comunidad": 1,
    "telefono": "0991234567",
    "estado": "ACTIVO"
}
```

**Resultado Esperado:**
- Status: 201 Created
- Socio creado con ID asignado
- Registro en bitácora de auditoría

### Caso de Prueba 7: Acceso No Autorizado
**Descripción:** Verificar que endpoints protegidos requieran autenticación.

**Request:**
```
GET /api/socios/
```

**Resultado Esperado:**
- Status: 401 Unauthorized
- Mensaje de error de autenticación

## Pruebas de Bitácora de Auditoría (T013)

### Caso de Prueba 8: Registro de Operaciones CRUD
**Descripción:** Verificar que todas las operaciones se registren en la bitácora.

**Pasos:**
1. Crear un nuevo socio
2. Actualizar el socio
3. Eliminar el socio
4. Consultar bitácora: GET /api/bitacora/

**Resultado Esperado:**
- Registros de CREAR, ACTUALIZAR, ELIMINAR en bitácora
- Información completa: usuario, fecha, tabla afectada, detalles

## Pruebas de Vista Móvil (T026)

### Caso de Prueba 9: Consulta de Socios en Móvil
**Descripción:** Verificar funcionamiento de la vista móvil de socios.

**Precondiciones:**
- Usuario autenticado
- Acceso desde dispositivo móvil o navegador móvil

**Pasos:**
1. Acceder a /mobile/socios/
2. Ingresar término de búsqueda
3. Verificar resultados filtrados

**Resultado Esperado:**
- Interfaz optimizada para móviles
- Búsqueda funcional por nombre, apellido, cédula
- Lista de socios con información completa

### Caso de Prueba 10: Búsqueda sin Resultados
**Descripción:** Verificar manejo de búsquedas sin resultados.

**Pasos:**
1. Ingresar término que no existe en la base de datos
2. Ejecutar búsqueda

**Resultado Esperado:**
- Mensaje: "No se encontraron socios"
- Interfaz sigue siendo funcional

## Pruebas de Validación de Datos

### Caso de Prueba 11: Validación de Superficie de Parcela
**Descripción:** Verificar que la superficie de parcela sea mayor a 0.

**Request:**
```
POST /api/parcelas/
{
    "socio": 1,
    "codigo_parcela": "PAR-001",
    "superficie_hectareas": 0,
    "latitud": -16.5,
    "longitud": -68.1
}
```

**Resultado Esperado:**
- Status: 400 Bad Request
- Mensaje de error: "La superficie debe ser mayor a 0"

### Caso de Prueba 12: Validación de Campos Requeridos
**Descripción:** Verificar validación de campos obligatorios.

**Request:**
```
POST /api/socios/
{
    "cedula": "",
    "usuario": {
        "usuario": "",
        "password": ""
    }
}
```

**Resultado Esperado:**
- Status: 400 Bad Request
- Mensaje de error con campos faltantes

## Pruebas de Rendimiento

### Caso de Prueba 13: Carga de Datos Grandes
**Descripción:** Verificar rendimiento con gran cantidad de registros.

**Precondiciones:**
- Base de datos con 1000+ registros

**Pasos:**
1. Solicitar lista completa de socios
2. Medir tiempo de respuesta

**Resultado Esperado:**
- Tiempo de respuesta < 2 segundos
- Datos paginados correctamente

## Checklist de Pruebas de Regresión

- [ ] Login funciona correctamente
- [ ] Logout limpia la sesión
- [ ] API endpoints responden correctamente
- [ ] Bitácora registra todas las operaciones
- [ ] Validaciones de datos funcionan
- [ ] Interfaz web carga correctamente
- [ ] Vista móvil es responsive
- [ ] Filtros de permisos funcionan (usuario normal vs admin)
- [ ] Manejo de errores es apropiado
- [ ] CORS está configurado correctamente