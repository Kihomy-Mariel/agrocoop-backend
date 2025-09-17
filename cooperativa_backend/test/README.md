# Estructura de Tests - Cooperativa Backend

Esta carpeta contiene todos los tests del sistema organizados por Caso de Uso (CU).

## Estructura de Carpetas

```
test/
├── CU1/                    # Autenticación, Login y Sesión Básica
│   ├── __init__.py
│   ├── test_auth.py        # Tests de autenticación y login
│   ├── test_bitacora.py    # Tests de auditoría básica
│   └── test_models.py      # Tests de modelos básicos
├── CU2/                    # Logout y Sesión Avanzada
│   ├── __init__.py
│   ├── test_cu2_logout.py  # Tests de logout
│   └── test_cu2_bitacora.py # Tests de auditoría extendida
├── CU3/                    # Gestión de Socios, Usuarios, Roles
│   ├── __init__.py
│   ├── test_socios.py      # Tests de gestión de socios
│   ├── test_cultivos.py    # Tests de cultivos (relacionado con socios)
│   └── test_parcelas.py    # Tests de parcelas (relacionado con socios)
├── basic_tests.py          # Tests básicos del sistema
├── tests_backup.py         # Backup de tests anteriores
├── Test_Cases.md          # Documentación de casos de test
└── __pycache__/           # Archivos compilados de Python
```

## Casos de Uso

### CU1: Autenticación, Login y Sesión Básica
- **Objetivo:** Validar el sistema de autenticación básico
- **Cobertura:**
  - Login de usuarios
  - Validación de credenciales
  - Gestión básica de sesiones
  - Auditoría inicial de operaciones

### CU2: Logout y Sesión Avanzada
- **Objetivo:** Validar funcionalidades avanzadas de sesión
- **Cobertura:**
  - Logout seguro
  - Gestión avanzada de sesiones
  - Auditoría extendida de operaciones
  - Manejo de tokens y permisos

### CU3: Gestión de Socios, Usuarios, Roles
- **Objetivo:** Validar gestión completa de socios y usuarios
- **Cobertura:**
  - CRUD de socios
  - Gestión de usuarios
  - Validaciones de datos
  - Búsquedas avanzadas
  - Reportes
  - Gestión de roles y permisos

## Ejecutar Tests

### Ejecutar todos los tests:
```bash
python manage.py test test/
```

### Ejecutar tests de un CU específico:
```bash
# CU1
python manage.py test test.CU1

# CU2
python manage.py test test.CU2

# CU3
python manage.py test test.CU3
```

### Ejecutar un test específico:
```bash
# Test específico
python manage.py test test.CU1.test_auth.AuthTest.test_login_success

# Todos los tests de un archivo
python manage.py test test.CU3.test_socios
```

## Convenciones de Nomenclatura

- **Archivos:** `test_[funcionalidad].py`
- **Clases:** `[Funcionalidad]Test`
- **Métodos:** `test_[descripcion_del_test]`
- **CU específicos:** `test_cu[numero]_[funcionalidad].py`

## Cobertura de Tests

Los tests cubren:
- ✅ Modelos y validaciones
- ✅ Serializers y transformación de datos
- ✅ Views y endpoints API
- ✅ Autenticación y permisos
- ✅ Auditoría y logging
- ✅ Validaciones de negocio
- ✅ Manejo de errores
- ✅ Integración entre componentes

## Mantenimiento

- **Agregar nuevos tests:** Colocar en la carpeta del CU correspondiente
- **Actualizar tests:** Modificar los archivos existentes según cambios en el código
- **Documentación:** Actualizar este README cuando se agreguen nuevos CUs
- **Backup:** Mantener `tests_backup.py` como respaldo de versiones anteriores