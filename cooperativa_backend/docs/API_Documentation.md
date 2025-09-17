# Documentación de la API - Sistema de Gestión Cooperativa

## Descripción General
Esta API REST proporciona funcionalidades completas para la gestión de una cooperativa agrícola, incluyendo autenticación, gestión de usuarios, socios, parcelas y cultivos.

## Estructura del Proyecto

```
Backend_Django/
├── cooperativa_Back/
│   ├── manage.py
│   ├── cooperativa_Back/
│   │   ├── __init__.py
│   │   ├── settings.py          # Configuración de Django
│   │   ├── urls.py             # URLs principales
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── cooperativa/
│   │   ├── models.py           # Modelos de datos
│   │   ├── serializers.py      # Serializers DRF
│   │   ├── views.py            # Vistas y ViewSets
│   │   ├── urls.py             # URLs de la app
│   │   ├── admin.py            # Configuración admin
│   │   └── apps.py
│   ├── docs/
│   │   └── API_Documentation.md # Esta documentación
│   └── test/
│       ├── CU1/                # Tests CU1: Autenticación
│       ├── CU2/                # Tests CU2: Logout/Sesión
│       ├── CU3/                # Tests CU3: Gestión Socios
│       ├── basic_tests.py
│       ├── tests_backup.py
│       ├── Test_Cases.md
│       └── README.md           # Documentación de tests
```

## Estructura de Tests por Caso de Uso

Los tests están organizados en carpetas por Caso de Uso para mantener una estructura clara y modular:

### CU1: Autenticación, Login y Sesión Básica
- **Ubicación:** `test/CU1/`
- **Archivos:** `test_auth.py`, `test_bitacora.py`, `test_models.py`
- **Cobertura:** Login, validación de credenciales, sesiones básicas, auditoría inicial

### CU2: Logout y Sesión Avanzada
- **Ubicación:** `test/CU2/`
- **Archivos:** `test_cu2_logout.py`, `test_cu2_bitacora.py`
- **Cobertura:** Logout seguro, gestión avanzada de sesiones, auditoría extendida

### CU3: Gestión de Socios, Usuarios, Roles
- **Ubicación:** `test/CU3/`
- **Archivos:** `test_socios.py`, `test_cultivos.py`, `test_parcelas.py`
- **Cobertura:** CRUD de socios, validaciones, búsquedas, reportes, gestión de usuarios

Para más detalles sobre la estructura de tests, consulte `test/README.md`.

## Casos de Uso

### CU1: Iniciar Sesión (Web/Móvil)
**Descripción:**  
El Caso de Uso CU1 permite a los usuarios autenticarse en el sistema de gestión cooperativa desde interfaces web o móviles. Este proceso valida las credenciales del usuario y establece una sesión segura para acceder a las funcionalidades del sistema.

**Objetivos:**
- Validar credenciales de usuario (usuario y contraseña)
- Establecer sesión de usuario autenticado
- Proporcionar token CSRF para operaciones seguras
- Registrar el inicio de sesión en la bitácora de auditoría
- Gestionar intentos fallidos de login (bloqueo después de 5 intentos)

**Actores:**
- Usuario registrado (socio, administrador, etc.)
- Sistema de autenticación

**Precondiciones:**
- El usuario debe estar registrado en el sistema
- La cuenta debe estar en estado "ACTIVO"
- No debe haber bloqueo por intentos fallidos

**Flujo Principal:**
1. El usuario ingresa sus credenciales (usuario y contraseña)
2. El sistema valida las credenciales contra la base de datos
3. Si son válidas, se crea una sesión de usuario
4. Se genera un token CSRF para operaciones posteriores
5. Se registra el evento en la bitácora de auditoría
6. Se devuelve la información del usuario y el token

**Flujos Alternativos:**
- **Credenciales Inválidas:** Se incrementa el contador de intentos fallidos. Después de 5 intentos, la cuenta se bloquea temporalmente.
- **Cuenta Inactiva:** Se muestra mensaje de error indicando que la cuenta está inactiva.
- **Cuenta Bloqueada:** Se informa al usuario sobre el bloqueo y se sugiere contactar al administrador.

**Postcondiciones:**
- Usuario autenticado con sesión activa
- Token CSRF disponible para operaciones API
- Registro de auditoría creado

**Guía de Implementación:**

#### Para Frontend Web (React):
```javascript
// Función de login
const loginUsuario = async (username, password) => {
  try {
    const response = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken() // Si es necesario
      },
      credentials: 'include', // Para incluir cookies de sesión
      body: JSON.stringify({
        username: username,
        password: password
      })
    });

    const data = await response.json();

    if (response.ok) {
      // Login exitoso
      console.log('Usuario autenticado:', data.usuario);
      // Guardar información en localStorage o estado global
      localStorage.setItem('user', JSON.stringify(data.usuario));
      // Redirigir al dashboard
      window.location.href = '/dashboard';
    } else {
      // Manejar error
      console.error('Error de login:', data.error);
      // Mostrar mensaje de error al usuario
    }
  } catch (error) {
    console.error('Error de conexión:', error);
  }
};

// Verificar estado de sesión
const verificarSesion = async () => {
  try {
    const response = await fetch('/api/auth/status/', {
      credentials: 'include'
    });
    const data = await response.json();
    
    if (data.autenticado) {
      console.log('Sesión activa para:', data.usuario);
      return true;
    } else {
      console.log('Sesión inactiva');
      return false;
    }
  } catch (error) {
    console.error('Error al verificar sesión:', error);
    return false;
  }
};
```

#### Para Aplicación Móvil (Flutter):
```dart
// Servicio de autenticación
class AuthService {
  static const String baseUrl = 'http://localhost:8000/api';

  // Método de login
  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        // Login exitoso
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('user', jsonEncode(data['usuario']));
        await prefs.setString('csrf_token', data['csrf_token']);
        
        return {
          'success': true,
          'usuario': data['usuario'],
          'csrf_token': data['csrf_token']
        };
      } else {
        // Error de login
        return {
          'success': false,
          'error': data['error'] ?? 'Error desconocido'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Error de conexión: $e'
      };
    }
  }

  // Verificar sesión
  static Future<bool> verificarSesion() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      if (token == null) return false;

      final response = await http.get(
        Uri.parse('$baseUrl/auth/status/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      final data = jsonDecode(response.body);
      return data['autenticado'] ?? false;
    } catch (e) {
      return false;
    }
  }

  // Logout
  static Future<void> logout() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      await http.post(
        Uri.parse('$baseUrl/auth/logout/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );
    } catch (e) {
      // Ignorar errores de logout
    } finally {
      // Limpiar datos locales
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('user');
      await prefs.remove('csrf_token');
    }
  }
}

// Widget de Login
class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() => _isLoading = true);

    final result = await AuthService.login(
      _usernameController.text,
      _passwordController.text
    );

    setState(() => _isLoading = false);

    if (result['success']) {
      // Login exitoso
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      // Mostrar error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error']))
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Iniciar Sesión - Cooperativa')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _usernameController,
              decoration: InputDecoration(
                labelText: 'Usuario',
                border: OutlineInputBorder()
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'Contraseña',
                border: OutlineInputBorder()
              ),
              obscureText: true,
            ),
            SizedBox(height: 24),
            _isLoading
              ? CircularProgressIndicator()
              : ElevatedButton(
                  onPressed: _login,
                  child: Text('Iniciar Sesión'),
                  style: ElevatedButton.styleFrom(
                    minimumSize: Size(double.infinity, 50)
                  ),
                ),
          ],
        ),
      ),
    );
  }
}
```

**Consideraciones de Seguridad para CU1:**
- Las contraseñas se almacenan hasheadas usando PBKDF2
- Se implementa protección contra ataques de fuerza bruta con límite de intentos
- Los tokens CSRF se generan automáticamente por Django
- Todas las sesiones tienen tiempo de expiración configurable
- Se registra cada intento de login (exitoso o fallido) en la bitácora

**Manejo de Errores en CU1:**
- **Credenciales Inválidas:** Mensaje genérico para evitar enumeración de usuarios
- **Cuenta Bloqueada:** Indicar tiempo de espera o contacto con administrador
- **Error de Conexión:** Reintentar automáticamente o mostrar opción manual
- **Sesión Expirada:** Redirigir automáticamente al login

**Pruebas Recomendadas:**
1. Login con credenciales válidas
2. Login con usuario inexistente
3. Login con contraseña incorrecta
4. Múltiples intentos fallidos (verificar bloqueo)
5. Verificación de estado de sesión
6. Logout y verificación de invalidación de sesión

### CU2: Cerrar Sesión (Web/Móvil)
**Descripción:**  
El Caso de Uso CU2 permite a los usuarios cerrar su sesión activa en el sistema de gestión cooperativa desde interfaces web o móviles. Este proceso finaliza la sesión del usuario, limpia los datos de autenticación y registra la actividad en la bitácora de auditoría extendida.

**Objetivos:**
- Finalizar la sesión activa del usuario
- Limpiar datos de autenticación del cliente
- Registrar el cierre de sesión en bitácora extendida
- Invalidar tokens de sesión si es necesario
- Proporcionar funcionalidades avanzadas de gestión de sesiones
- Permitir a administradores forzar cierre de sesiones de otros usuarios

**Actores:**
- Usuario autenticado (socio, administrador, etc.)
- Administrador del sistema (para operaciones avanzadas)
- Sistema de gestión de sesiones

**Precondiciones:**
- El usuario debe tener una sesión activa
- Debe estar autenticado en el sistema
- Para operaciones administrativas: el usuario debe tener permisos de administrador

**Flujo Principal:**
1. El usuario solicita cerrar sesión
2. El sistema registra el evento en bitácora extendida
3. Se invalidan los tokens de sesión
4. Se limpia la información de autenticación del cliente
5. Se confirma el cierre exitoso de la sesión

**Flujo Principal (Administrador):**
1. El administrador selecciona un usuario
2. El sistema verifica permisos de administrador
3. Se invalidan todas las sesiones del usuario seleccionado
4. Se registra la acción en bitácora extendida
5. Se notifica el resultado de la operación

**Flujos Alternativos:**
- **Sesión ya expirada:** Se registra el intento y se confirma
- **Usuario sin permisos:** Se deniega la operación administrativa
- **Usuario no encontrado:** Error al intentar forzar logout
- **Error de conexión:** Se registra el intento fallido

**Postcondiciones:**
- Sesión del usuario finalizada
- Tokens de autenticación invalidados
- Registro de auditoría creado con detalles completos
- Cliente debe volver a autenticarse para acceder

**Guía de Implementación:**

#### Para Frontend Web (React) - CU2:
```javascript
// Función de logout
const logoutUsuario = async () => {
  try {
    const response = await fetch('/api/auth/logout/', {
      method: 'POST',
      credentials: 'include', // Para incluir cookies de sesión
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (response.ok) {
      // Logout exitoso
      console.log('Sesión cerrada exitosamente');
      
      // Limpiar datos locales
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      
      // Redirigir al login
      window.location.href = '/login';
    } else {
      console.error('Error al cerrar sesión');
    }
  } catch (error) {
    console.error('Error de conexión:', error);
    // Aun así limpiar datos locales
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
};

// Invalidar todas las sesiones
const invalidarSesiones = async () => {
  try {
    const response = await fetch('/api/auth/invalidate-sessions/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log(`Se invalidaron ${data.sesiones_invalidada} sesiones`);
      alert(`Sesiones invalidadas: ${data.sesiones_invalidada}`);
    } else {
      console.error('Error al invalidar sesiones:', data.error);
    }
  } catch (error) {
    console.error('Error de conexión:', error);
  }
};

// Información detallada de sesión
const obtenerInfoSesion = async () => {
  try {
    const response = await fetch('/api/auth/session-info/', {
      credentials: 'include'
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Información de sesión:', data);
      return data;
    } else {
      console.error('Error al obtener información de sesión');
      return null;
    }
  } catch (error) {
    console.error('Error de conexión:', error);
    return null;
  }
};

// Función administrativa para forzar logout
const forzarLogoutUsuario = async (userId) => {
  try {
    const response = await fetch(`/api/auth/force-logout/${userId}/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log(`Usuario ${data.usuario_afectado} desconectado`);
      alert(`Usuario ${data.usuario_afectado} ha sido desconectado`);
    } else {
      console.error('Error al forzar logout:', data.error);
      alert(`Error: ${data.error}`);
    }
  } catch (error) {
    console.error('Error de conexión:', error);
  }
};
```

#### Para Aplicación Móvil (Flutter) - CU2:
```dart
// Servicio de autenticación extendido
class AuthService {
  static const String baseUrl = 'http://localhost:8000/api';

  // Logout mejorado
  static Future<bool> logout() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/auth/logout/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      // Limpiar datos locales independientemente del resultado
      await prefs.remove('user');
      await prefs.remove('csrf_token');
      
      return response.statusCode == 200;
    } catch (e) {
      // Limpiar datos locales incluso si hay error
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('user');
      await prefs.remove('csrf_token');
      
      return false;
    }
  }

  // Invalidar todas las sesiones
  static Future<Map<String, dynamic>> invalidateAllSessions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/auth/invalidate-sessions/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Información detallada de sesión
  static Future<Map<String, dynamic>?> getSessionInfo() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.get(
        Uri.parse('$baseUrl/auth/session-info/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  // Forzar logout de usuario (solo admin)
  static Future<Map<String, dynamic>> forceLogoutUser(int userId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/auth/force-logout/$userId/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }
}

// Widget de Logout mejorado
class ProfileScreen extends StatefulWidget {
  @override
  _ProfileScreenState createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _sessionInfo;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadSessionInfo();
  }

  Future<void> _loadSessionInfo() async {
    final info = await AuthService.getSessionInfo();
    setState(() {
      _sessionInfo = info;
    });
  }

  Future<void> _logout() async {
    setState(() => _isLoading = true);
    
    final success = await AuthService.logout();
    
    setState(() => _isLoading = false);
    
    if (success) {
      Navigator.pushReplacementNamed(context, '/login');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cerrar sesión'))
      );
    }
  }

  Future<void> _invalidateSessions() async {
    setState(() => _isLoading = true);
    
    final result = await AuthService.invalidateAllSessions();
    
    setState(() => _isLoading = false);
    
    if (result.containsKey('sesiones_invalidada')) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Sesiones invalidadas: ${result['sesiones_invalidada']}'))
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${result['error']}'))
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Perfil')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_sessionInfo != null) ...[
              Text('Usuario: ${_sessionInfo!['usuario']['nombres']} ${_sessionInfo!['usuario']['apellidos']}'),
              Text('IP: ${_sessionInfo!['ip_address']}'),
              Text('User Agent: ${_sessionInfo!['user_agent']}'),
              Text('Sesión expira: ${_sessionInfo!['session_expiry']}'),
              SizedBox(height: 20),
            ],
            
            ElevatedButton(
              onPressed: _isLoading ? null : _invalidateSessions,
              child: Text('Invalidar Todas las Sesiones'),
              style: ElevatedButton.styleFrom(
                minimumSize: Size(double.infinity, 50)
              ),
            ),
            
            SizedBox(height: 16),
            
            ElevatedButton(
              onPressed: _isLoading ? null : _logout,
              child: _isLoading ? CircularProgressIndicator() : Text('Cerrar Sesión'),
              style: ElevatedButton.styleFrom(
                minimumSize: Size(double.infinity, 50),
                backgroundColor: Colors.red
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

**Consideraciones de Seguridad para CU2:**
- Se registra cada cierre de sesión en bitácora extendida con IP y User-Agent
- Los administradores pueden forzar cierre de sesiones de otros usuarios
- Se invalidan todas las sesiones del usuario al hacer logout
- Se limpian tokens y datos de autenticación del cliente
- Protección contra ataques de sesión hijacking

**Manejo de Errores en CU2:**
- **Sesión ya expirada:** Mensaje informativo, no error
- **Usuario sin permisos:** Error 403 con mensaje claro
- **Usuario no encontrado:** Error 404 para operaciones administrativas
- **Error de conexión:** Limpiar datos locales y redirigir a login
- **Token inválido:** Redirigir automáticamente a login

**Pruebas Recomendadas para CU2:**
1. Logout exitoso desde sesión activa
2. Logout sin autenticación (debe fallar)
3. Invalidar todas las sesiones del usuario
4. Verificar información detallada de sesión
5. Forzar logout por administrador (usuario con permisos)
6. Forzar logout por usuario normal (debe fallar)
7. Forzar logout de usuario inexistente
8. Verificar registros en bitácora de auditoría
9. Verificar limpieza de datos locales después del logout
10. Probar logout con error de conexión

## Base URL
```
http://localhost:8000/api/
```

## Autenticación
La API utiliza autenticación basada en sesiones de Django. Los endpoints requieren autenticación a menos que se especifique lo contrario.

### Endpoints de Autenticación

#### POST /api/auth/login/
Inicia sesión en el sistema.

**Request Body:**
```json
{
    "username": "usuario",
    "password": "contraseña"
}
```

**Response (éxito):**
```json
{
    "mensaje": "Login exitoso",
    "usuario": {
        "id": 1,
        "usuario": "admin",
        "nombre": "Administrador",
        "apellido": "Sistema",
        "email": "admin@cooperativa.com",
        "estado": "ACTIVO"
    },
    "csrf_token": "token_csrf"
}
```

**Response (error):**
```json
{
    "error": "Credenciales inválidas"
}
```

#### POST /api/auth/logout/
Cierra la sesión actual y registra el evento en bitácora extendida.

**Response:**
```json
{
    "mensaje": "Sesión cerrada exitosamente"
}
```

#### GET /api/auth/status/
Verifica el estado de la sesión actual.

**Response:**
```json
{
    "autenticado": true,
    "usuario": {
        "id": 1,
        "usuario": "admin",
        "nombre": "Administrador",
        "apellido": "Sistema"
    }
}
```

#### POST /api/auth/invalidate-sessions/
Invalida todas las sesiones del usuario actual (CU2).

**Response:**
```json
{
    "mensaje": "Se invalidaron X sesiones",
    "sesiones_invalidada": 2
}
```

#### GET /api/auth/session-info/
Obtiene información detallada de la sesión actual (CU2).

**Response:**
```json
{
    "usuario": {...},
    "session_id": "abc123",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_expiry": "2025-09-17T21:36:22Z",
    "is_secure": false,
    "autenticado": true
}
```

#### POST /api/auth/force-logout/{user_id}/
Permite a administradores forzar el cierre de sesión de otro usuario (CU2).

**Response:**
```json
{
    "mensaje": "Se invalidaron X sesiones del usuario username",
    "usuario_afectado": "username",
    "sesiones_invalidada": 1
}
```

## Endpoints de Datos

### Roles
- **GET** `/api/roles/` - Lista todos los roles
- **POST** `/api/roles/` - Crea un nuevo rol
- **GET** `/api/roles/{id}/` - Obtiene un rol específico
- **PUT** `/api/roles/{id}/` - Actualiza un rol
- **DELETE** `/api/roles/{id}/` - Elimina un rol

### Usuarios
- **GET** `/api/usuarios/` - Lista todos los usuarios
- **POST** `/api/usuarios/` - Crea un nuevo usuario
- **GET** `/api/usuarios/{id}/` - Obtiene un usuario específico
- **PUT** `/api/usuarios/{id}/` - Actualiza un usuario
- **DELETE** `/api/usuarios/{id}/` - Elimina un usuario

**Campos para crear usuario:**
```json
{
    "usuario": "nuevo_usuario",
    "password": "contraseña_segura",
    "nombre": "Nombre",
    "apellido": "Apellido",
    "email": "usuario@email.com",
    "estado": "ACTIVO"
}
```

### Comunidades
- **GET** `/api/comunidades/` - Lista todas las comunidades
- **POST** `/api/comunidades/` - Crea una nueva comunidad
- **GET** `/api/comunidades/{id}/` - Obtiene una comunidad específica
- **PUT** `/api/comunidades/{id}/` - Actualiza una comunidad
- **DELETE** `/api/comunidades/{id}/` - Elimina una comunidad

### Socios
- **GET** `/api/socios/` - Lista todos los socios
- **POST** `/api/socios/` - Crea un nuevo socio
- **GET** `/api/socios/{id}/` - Obtiene un socio específico
- **PUT** `/api/socios/{id}/` - Actualiza un socio
- **DELETE** `/api/socios/{id}/` - Elimina un socio

### Parcelas
- **GET** `/api/parcelas/` - Lista todas las parcelas
- **POST** `/api/parcelas/` - Crea una nueva parcela
- **GET** `/api/parcelas/{id}/` - Obtiene una parcela específica
- **PUT** `/api/parcelas/{id}/` - Actualiza una parcela
- **DELETE** `/api/parcelas/{id}/` - Elimina una parcela

**Campos para parcela:**
```json
{
    "socio": 1,
    "codigo_parcela": "PAR-001",
    "superficie_hectareas": 5.5,
    "latitud": -16.5,
    "longitud": -68.1,
    "estado": "ACTIVA"
}
```

### Cultivos
- **GET** `/api/cultivos/` - Lista todos los cultivos
- **POST** `/api/cultivos/` - Crea un nuevo cultivo
- **GET** `/api/cultivos/{id}/` - Obtiene un cultivo específico
- **PUT** `/api/cultivos/{id}/` - Actualiza un cultivo
- **DELETE** `/api/cultivos/{id}/` - Elimina un cultivo

### Bitácora de Auditoría
- **GET** `/api/bitacora/` - Lista registros de auditoría

## Códigos de Estado HTTP
- **200 OK** - Solicitud exitosa
- **201 Created** - Recurso creado exitosamente
- **400 Bad Request** - Datos inválidos en la solicitud
- **401 Unauthorized** - Autenticación requerida
- **403 Forbidden** - Permisos insuficientes
- **404 Not Found** - Recurso no encontrado
- **500 Internal Server Error** - Error del servidor

## Consideraciones de Seguridad
1. Todas las operaciones requieren autenticación
2. Los usuarios solo pueden acceder a sus propios datos (socios a sus parcelas/cultivos)
3. Se registra toda actividad en la bitácora de auditoría
4. Las cuentas se bloquean después de 5 intentos fallidos de login
5. Las contraseñas deben cumplir con políticas de seguridad

## Interfaz Web
Además de la API REST, el sistema incluye interfaces web:

- **Login**: `/login/` - Formulario de inicio de sesión
- **Dashboard**: `/dashboard/` - Panel principal después del login
- **Vista Móvil Socios**: `/mobile/socios/` - Consulta de socios optimizada para móviles

## Tecnologías Utilizadas
- Django 5.0
- Django REST Framework
- PostgreSQL

## Integración con Frontend

### React (JavaScript/TypeScript)
```javascript
// Configuración base
const API_BASE_URL = 'http://localhost:8000/api';

// Login
const login = async (username, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (data.usuario) {
      localStorage.setItem('token', data.csrf_token);
      localStorage.setItem('user', JSON.stringify(data.usuario));
    }
    return data;
  } catch (error) {
    console.error('Error en login:', error);
    return { error: 'Error de conexión' };
  }
};

// Obtener datos con token
const getData = async (endpoint) => {
  const token = localStorage.getItem('token');
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return await response.json();
  } catch (error) {
    console.error('Error al obtener datos:', error);
    return { error: 'Error de conexión' };
  }
};

// Uso
const handleLogin = async () => {
  const result = await login('admin', 'password');
  if (result.usuario) {
    // Login exitoso
    const socios = await getData('/socios/');
    console.log('Socios:', socios);
  }
};
```

### Flutter (Dart)
```dart
// Configuración base
const String apiBaseUrl = 'http://localhost:8000/api';

// Servicio de autenticación
class AuthService {
  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión'};
    }
  }

  static Future<Map<String, dynamic>> getData(String endpoint) async {
    final token = await _getToken();
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl$endpoint'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión'};
    }
  }

  static Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }
}

// Widget de ejemplo
class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  Future<void> _login() async {
    final result = await AuthService.login(
      _usernameController.text,
      _passwordController.text
    );

    if (result.containsKey('usuario')) {
      // Guardar token
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', result['csrf_token']);
      await prefs.setString('user', jsonEncode(result['usuario']));

      // Navegar al dashboard
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      // Mostrar error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error'] ?? 'Error desconocido'))
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Login Cooperativa')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _usernameController,
              decoration: InputDecoration(labelText: 'Usuario'),
            ),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'Contraseña'),
              obscureText: true,
            ),
            ElevatedButton(
              onPressed: _login,
              child: Text('Iniciar Sesión'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## Manejo de Errores

### Errores Comunes
- **401 Unauthorized**: Token expirado o inválido
- **403 Forbidden**: Usuario sin permisos para la operación
- **400 Bad Request**: Datos inválidos en la solicitud
- **404 Not Found**: Recurso no existe

### Estrategia de Reintento
```javascript
// React - Reintento automático
const apiCall = async (url, options, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.status === 401) {
        // Token expirado, redirigir a login
        localStorage.removeItem('token');
        window.location.href = '/login';
        return;
      }
      return await response.json();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

### CU3: Gestionar Socios (Alta, Edición, Inhabilitar/Reactivar)
**Descripción:**  
El Caso de Uso CU3 permite la gestión completa de socios en el sistema de cooperativa agrícola. Incluye operaciones de alta, edición, inhabilitación/reactivación de socios, así como funcionalidades avanzadas de búsqueda, filtros y reportes. Este CU es fundamental para el mantenimiento de la base de datos de miembros de la cooperativa.

**Objetivos:**
- Gestionar el ciclo de vida completo de los socios (alta, modificación, baja lógica)
- Validar datos de entrada para mantener la integridad de la información
- Proporcionar herramientas avanzadas de búsqueda y filtrado
- Generar reportes sobre el estado de los socios
- Mantener auditoría completa de todas las operaciones
- Gestionar usuarios asociados a los socios
- Validar duplicados y restricciones de negocio

**Actores:**
- Administrador del sistema
- Usuario con permisos de gestión de socios
- Sistema de validación de datos

**Precondiciones:**
- Usuario debe estar autenticado y tener permisos adecuados
- Para operaciones administrativas: permisos de administrador requeridos
- Datos de comunidades deben existir para asignar socios

**Flujo Principal - Alta de Socio:**
1. Usuario solicita crear nuevo socio
2. Sistema valida permisos del usuario
3. Usuario ingresa datos del socio (datos personales + usuario)
4. Sistema valida formato y unicidad de datos (CI/NIT, email, usuario)
5. Sistema crea usuario y socio asociados
6. Sistema registra operación en bitácora de auditoría
7. Sistema confirma creación exitosa

**Flujo Principal - Edición de Socio:**
1. Usuario selecciona socio a editar
2. Sistema carga datos actuales del socio
3. Usuario modifica datos necesarios
4. Sistema valida cambios (unicidad, formato, reglas de negocio)
5. Sistema actualiza socio y usuario si es necesario
6. Sistema registra cambios en bitácora
7. Sistema confirma actualización exitosa

**Flujo Principal - Inhabilitar/Reactivar Socio:**
1. Usuario selecciona socio
2. Usuario elige acción (activar/desactivar)
3. Sistema valida permisos para la operación
4. Sistema cambia estado del socio y usuario asociado
5. Sistema registra cambio en bitácora con detalles
6. Sistema confirma cambio de estado

**Flujos Alternativos:**
- **Datos Inválidos:** Sistema muestra errores específicos por campo
- **Duplicados Encontrados:** Sistema indica campos que violan unicidad
- **Permisos Insuficientes:** Operación denegada con mensaje claro
- **Socio No Encontrado:** Error 404 con mensaje descriptivo
- **Error de Validación:** Lista detallada de errores por campo

**Postcondiciones:**
- Socio creado/modificado con estado correcto
- Usuario asociado actualizado si corresponde
- Registros de auditoría creados con detalles completos
- Estados sincronizados entre socio y usuario

**Guía de Implementación - CU3:**

#### Para Frontend Web (React):
```javascript
// Servicio de gestión de socios
class SocioService {
  static baseUrl = '/api';

  // Crear socio completo
  static async crearSocioCompleto(socioData) {
    try {
      const response = await fetch(`${this.baseUrl}/socios/crear-completo/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(socioData)
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Socio creado:', data);
        return { success: true, data };
      } else {
        console.error('Error al crear socio:', data);
        return { success: false, errors: data };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Activar/desactivar socio
  static async cambiarEstadoSocio(socioId, accion) {
    try {
      const response = await fetch(`${this.baseUrl}/socios/${socioId}/activar-desactivar/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ accion })
      });

      const data = await response.json();

      if (response.ok) {
        console.log(`Socio ${accion}do:`, data.socio);
        return { success: true, data };
      } else {
        console.error('Error al cambiar estado:', data);
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Búsqueda avanzada de socios
  static async buscarSociosAvanzado(filtros = {}) {
    try {
      const params = new URLSearchParams();
      
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params.append(key, value);
        }
      });

      const response = await fetch(`${this.baseUrl}/socios/buscar-avanzado/?${params}`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Buscar socios por cultivo
  static async buscarSociosPorCultivo(especie, estado = null) {
    try {
      const params = new URLSearchParams({ especie });
      if (estado) params.append('estado', estado);

      const response = await fetch(`${this.baseUrl}/socios/buscar-por-cultivo/?${params}`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Validar datos antes de crear/editar
  static async validarDatosSocio(datos) {
    try {
      const params = new URLSearchParams();
      
      Object.entries(datos).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await fetch(`${this.baseUrl}/validar/datos-socio/?${params}`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        return { valido: data.valido, mensaje: data.mensaje };
      } else {
        return { valido: false, errores: data.errores };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { valido: false, error: 'Error de conexión' };
    }
  }

  // Obtener reportes
  static async obtenerReporteSocios() {
    try {
      const response = await fetch(`${this.baseUrl}/reportes/usuarios-socios/`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }
}

// Componente de Gestión de Socios
class GestionSocios extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      socios: [],
      filtros: {
        nombre: '',
        apellido: '',
        ci_nit: '',
        comunidad: '',
        estado: '',
        codigo_interno: '',
        sexo: ''
      },
      loading: false,
      error: null
    };
  }

  componentDidMount() {
    this.cargarSocios();
  }

  async cargarSocios() {
    this.setState({ loading: true, error: null });
    
    const result = await SocioService.buscarSociosAvanzado(this.state.filtros);
    
    if (result.success) {
      this.setState({ 
        socios: result.data.results,
        loading: false 
      });
    } else {
      this.setState({ 
        error: result.error,
        loading: false 
      });
    }
  }

  handleFiltroChange = (campo, valor) => {
    this.setState(prevState => ({
      filtros: {
        ...prevState.filtros,
        [campo]: valor
      }
    }));
  }

  handleBuscar = () => {
    this.cargarSocios();
  }

  handleCambiarEstado = async (socioId, accion) => {
    const result = await SocioService.cambiarEstadoSocio(socioId, accion);
    
    if (result.success) {
      alert(`Socio ${accion === 'activar' ? 'activado' : 'desactivado'} exitosamente`);
      this.cargarSocios(); // Recargar lista
    } else {
      alert(`Error: ${result.error}`);
    }
  }

  render() {
    const { socios, filtros, loading, error } = this.state;

    return (
      <div className="gestion-socios">
        <h2>Gestión de Socios</h2>
        
        {/* Filtros */}
        <div className="filtros">
          <input
            type="text"
            placeholder="Nombre"
            value={filtros.nombre}
            onChange={(e) => this.handleFiltroChange('nombre', e.target.value)}
          />
          <input
            type="text"
            placeholder="Apellido"
            value={filtros.apellido}
            onChange={(e) => this.handleFiltroChange('apellido', e.target.value)}
          />
          <input
            type="text"
            placeholder="CI/NIT"
            value={filtros.ci_nit}
            onChange={(e) => this.handleFiltroChange('ci_nit', e.target.value)}
          />
          <select
            value={filtros.estado}
            onChange={(e) => this.handleFiltroChange('estado', e.target.value)}
          >
            <option value="">Todos los estados</option>
            <option value="ACTIVO">Activo</option>
            <option value="INACTIVO">Inactivo</option>
          </select>
          <button onClick={this.handleBuscar} disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>

        {/* Lista de Socios */}
        {error && <div className="error">{error}</div>}
        
        <div className="socios-list">
          {socios.map(socio => (
            <div key={socio.id} className="socio-card">
              <div className="socio-info">
                <h3>{socio.usuario_info.nombres} {socio.usuario_info.apellidos}</h3>
                <p>CI/NIT: {socio.usuario_info.ci_nit}</p>
                <p>Código: {socio.codigo_interno}</p>
                <p>Estado: {socio.estado}</p>
                <p>Comunidad: {socio.comunidad_nombre}</p>
              </div>
              <div className="socio-actions">
                <button 
                  onClick={() => this.handleCambiarEstado(socio.id, 'activar')}
                  disabled={socio.estado === 'ACTIVO'}
                >
                  Activar
                </button>
                <button 
                  onClick={() => this.handleCambiarEstado(socio.id, 'desactivar')}
                  disabled={socio.estado === 'INACTIVO'}
                >
                  Desactivar
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
}
```

#### Para Aplicación Móvil (Flutter) - CU3:
```dart
// Servicio de gestión de socios
class SocioService {
  static const String baseUrl = 'http://localhost:8000/api';

  // Crear socio completo
  static Future<Map<String, dynamic>> crearSocioCompleto(Map<String, dynamic> socioData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/socios/crear-completo/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode(socioData),
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Activar/desactivar socio
  static Future<Map<String, dynamic>> cambiarEstadoSocio(int socioId, String accion) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/socios/$socioId/activar-desactivar/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({'accion': accion}),
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Búsqueda avanzada
  static Future<Map<String, dynamic>> buscarSociosAvanzado(Map<String, String> filtros) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final params = filtros.entries
        .where((entry) => entry.value.isNotEmpty)
        .map((entry) => '${entry.key}=${Uri.encodeComponent(entry.value)}')
        .join('&');
      
      final response = await http.get(
        Uri.parse('$baseUrl/socios/buscar-avanzado/?$params'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Validar datos
  static Future<Map<String, dynamic>> validarDatosSocio(Map<String, String> datos) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final params = datos.entries
        .where((entry) => entry.value.isNotEmpty)
        .map((entry) => '${entry.key}=${Uri.encodeComponent(entry.value)}')
        .join('&');
      
      final response = await http.get(
        Uri.parse('$baseUrl/validar/datos-socio/?$params'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Obtener reportes
  static Future<Map<String, dynamic>> obtenerReporteSocios() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.get(
        Uri.parse('$baseUrl/reportes/usuarios-socios/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }
}

// Widget de Gestión de Socios
class GestionSociosScreen extends StatefulWidget {
  @override
  _GestionSociosScreenState createState() => _GestionSociosScreenState();
}

class _GestionSociosScreenState extends State<GestionSociosScreen> {
  List<dynamic> _socios = [];
  Map<String, String> _filtros = {
    'nombre': '',
    'apellido': '',
    'ci_nit': '',
    'estado': '',
    'codigo_interno': '',
  };
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _cargarSocios();
  }

  Future<void> _cargarSocios() async {
    setState(() => _isLoading = true);

    final result = await SocioService.buscarSociosAvanzado(_filtros);

    setState(() => _isLoading = false);

    if (result.containsKey('results')) {
      setState(() {
        _socios = result['results'];
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${result['error']}'))
      );
    }
  }

  Future<void> _cambiarEstadoSocio(int socioId, String accion) async {
    final result = await SocioService.cambiarEstadoSocio(socioId, accion);

    if (result.containsKey('mensaje')) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['mensaje']))
      );
      _cargarSocios(); // Recargar lista
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${result['error']}'))
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Gestión de Socios'),
        actions: [
          IconButton(
            icon: Icon(Icons.search),
            onPressed: _cargarSocios,
          ),
        ],
      ),
      body: Column(
        children: [
          // Filtros
          Padding(
            padding: EdgeInsets.all(8.0),
            child: Column(
              children: [
                TextField(
                  decoration: InputDecoration(
                    labelText: 'Nombre',
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (value) => _filtros['nombre'] = value,
                ),
                SizedBox(height: 8),
                TextField(
                  decoration: InputDecoration(
                    labelText: 'Apellido',
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (value) => _filtros['apellido'] = value,
                ),
                SizedBox(height: 8),
                TextField(
                  decoration: InputDecoration(
                    labelText: 'CI/NIT',
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (value) => _filtros['ci_nit'] = value,
                ),
                SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  decoration: InputDecoration(
                    labelText: 'Estado',
                    border: OutlineInputBorder(),
                  ),
                  value: _filtros['estado'],
                  items: [
                    DropdownMenuItem(value: '', child: Text('Todos')),
                    DropdownMenuItem(value: 'ACTIVO', child: Text('Activo')),
                    DropdownMenuItem(value: 'INACTIVO', child: Text('Inactivo')),
                  ],
                  onChanged: (value) => setState(() => _filtros['estado'] = value ?? ''),
                ),
              ],
            ),
          ),

          // Lista de Socios
          Expanded(
            child: _isLoading
              ? Center(child: CircularProgressIndicator())
              : ListView.builder(
                  itemCount: _socios.length,
                  itemBuilder: (context, index) {
                    final socio = _socios[index];
                    return Card(
                      margin: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${socio['usuario_info']['nombres']} ${socio['usuario_info']['apellidos']}',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            Text('CI/NIT: ${socio['usuario_info']['ci_nit']}'),
                            Text('Código: ${socio['codigo_interno'] ?? 'N/A'}'),
                            Text('Estado: ${socio['estado']}'),
                            Text('Comunidad: ${socio['comunidad_nombre'] ?? 'N/A'}'),
                            SizedBox(height: 8),
                            Row(
                              children: [
                                Expanded(
                                  child: ElevatedButton(
                                    onPressed: socio['estado'] == 'ACTIVO' ? null : () => _cambiarEstadoSocio(socio['id'], 'activar'),
                                    child: Text('Activar'),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: Colors.green,
                                    ),
                                  ),
                                ),
                                SizedBox(width: 8),
                                Expanded(
                                  child: ElevatedButton(
                                    onPressed: socio['estado'] == 'INACTIVO' ? null : () => _cambiarEstadoSocio(socio['id'], 'desactivar'),
                                    child: Text('Desactivar'),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: Colors.red,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Navegar a pantalla de crear socio
          Navigator.pushNamed(context, '/crear-socio');
        },
        child: Icon(Icons.add),
        tooltip: 'Crear Socio',
      ),
    );
  }
}
```

**Consideraciones de Seguridad para CU3:**
- Todas las operaciones requieren autenticación y permisos adecuados
- Se registra cada operación en bitácora de auditoría con detalles completos
- Validaciones de datos previenen inyección y datos malformados
- Verificación de unicidad en campos críticos (CI/NIT, email, usuario)
- Sincronización de estados entre usuario y socio
- Protección contra operaciones masivas no autorizadas

**Validaciones Implementadas en CU3:**
- **CI/NIT**: Formato válido, unicidad, longitud entre 6-12 dígitos
- **Email**: Formato válido, unicidad, dominios bloqueados
- **Usuario**: Unicidad, caracteres permitidos, longitud
- **Contraseña**: Fortaleza (mayúsculas, números), longitud mínima
- **Superficie**: Valor positivo, límites razonables
- **Coordenadas**: Valores geográficos válidos, ambas coordenadas requeridas
- **Edad**: Mínimo 18 años para socios
- **Fechas**: Fechas futuras para siembra, fechas pasadas no permitidas

**Manejo de Errores en CU3:**
- **Datos Inválidos:** Mensajes específicos por campo con formato claro
- **Duplicados:** Indicación exacta de qué campos violan unicidad
- **Permisos Insuficientes:** Mensaje claro sobre permisos requeridos
- **Recursos No Encontrados:** Error 404 con contexto específico
- **Errores de Conexión:** Reintento automático con retroceso exponencial
- **Validaciones de Negocio:** Mensajes descriptivos sobre reglas violadas

**Pruebas Recomendadas para CU3:**
1. Crear socio con datos válidos
2. Crear socio con datos inválidos (verificar validaciones)
3. Intentar crear socio con CI/NIT duplicado
4. Editar socio existente
5. Activar/desactivar socio
6. Búsqueda avanzada con múltiples filtros
7. Búsqueda por cultivo
8. Validación de datos antes de envío
9. Obtener reportes de usuarios y socios
10. Verificar registros en bitácora de auditoría
11. Probar permisos insuficientes
12. Validar límites de superficie y coordenadas

## Endpoints Adicionales - CU3

### Gestión de Socios

#### POST /api/socios/crear-completo/
Crea un socio completo con usuario incluido.

**Request Body:**
```json
{
    "ci_nit": "12345678",
    "nombres": "Juan",
    "apellidos": "Pérez",
    "email": "juan@email.com",
    "telefono": "77712345",
    "usuario_username": "jperez",
    "password": "SecurePass123",
    "codigo_interno": "SOC-001",
    "fecha_nacimiento": "1990-01-01",
    "sexo": "M",
    "direccion": "Calle 123",
    "comunidad": 1
}
```

**Response (éxito):**
```json
{
    "id": 1,
    "usuario": 1,
    "usuario_info": {...},
    "codigo_interno": "SOC-001",
    "fecha_nacimiento": "1990-01-01",
    "sexo": "M",
    "direccion": "Calle 123",
    "comunidad": 1,
    "comunidad_nombre": "Comunidad Central",
    "estado": "ACTIVO",
    "creado_en": "2025-09-17T10:00:00Z"
}
```

#### POST /api/socios/{id}/activar-desactivar/
Activa o desactiva un socio.

**Request Body:**
```json
{
    "accion": "activar"  // o "desactivar"
}
```

**Response:**
```json
{
    "mensaje": "Socio activado exitosamente",
    "socio": {...}
}
```

#### GET /api/socios/buscar-avanzado/
Búsqueda avanzada de socios con filtros múltiples.

**Parámetros de Query:**
- `nombre`: Filtrar por nombre
- `apellido`: Filtrar por apellido
- `ci_nit`: Filtrar por CI/NIT
- `comunidad`: ID de comunidad
- `estado`: Estado del socio
- `codigo_interno`: Código interno
- `sexo`: Sexo del socio
- `page`: Página (paginación)
- `page_size`: Tamaño de página

**Response:**
```json
{
    "count": 25,
    "page": 1,
    "page_size": 20,
    "total_pages": 2,
    "results": [...]
}
```

#### GET /api/socios/buscar-por-cultivo/
Busca socios que tienen cultivos de una especie específica.

**Parámetros de Query:**
- `especie`: Especie del cultivo (requerido)
- `estado`: Estado del cultivo (opcional)

**Response:**
```json
{
    "count": 15,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "filtros": {
        "especie_cultivo": "Maíz",
        "estado_cultivo": "ACTIVO"
    },
    "results": [...]
}
```

### Gestión de Usuarios

#### POST /api/usuarios/{id}/activar-desactivar/
Activa o desactiva un usuario.

**Request Body:**
```json
{
    "accion": "activar"  // o "desactivar"
}
```

**Response:**
```json
{
    "mensaje": "Usuario activado exitosamente",
    "usuario": {...}
}
```

### Reportes

#### GET /api/reportes/usuarios-socios/
Obtiene reportes generales de usuarios y socios.

**Response:**
```json
{
    "resumen_general": {
        "usuarios_total": 50,
        "usuarios_activos": 45,
        "usuarios_inactivos": 3,
        "usuarios_bloqueados": 2,
        "socios_total": 35,
        "socios_activos": 32,
        "socios_inactivos": 3
    },
    "socios_por_comunidad": [
        {"nombre": "Comunidad A", "num_socios": 15},
        {"nombre": "Comunidad B", "num_socios": 12}
    ],
    "usuarios_por_rol": [
        {"nombre": "Socio", "num_usuarios": 30},
        {"nombre": "Admin", "num_usuarios": 5}
    ],
    "socios_por_mes": [
        {"mes": "2025-01-01", "count": 5},
        {"mes": "2025-02-01", "count": 8}
    ],
    "porcentajes": {
        "usuarios_activos_pct": 90.0,
        "socios_activos_pct": 91.4
    }
}
```

### Validación de Datos

#### GET /api/validar/datos-socio/
Valida datos antes de crear/editar un socio.

**Parámetros de Query:**
- `ci_nit`: CI/NIT a validar
- `email`: Email a validar
- `usuario`: Usuario a validar
- `codigo_interno`: Código interno a validar

**Response (válido):**
```json
{
    "valido": true,
    "mensaje": "Todos los datos son válidos"
}
```

**Response (inválido):**
```json
{
    "valido": false,
    "errores": {
        "ci_nit": "Ya existe un usuario con este CI/NIT",
        "email": "Ya existe un usuario con este email"
    }
}
```

## Acciones en ViewSets - CU3

### SocioViewSet
- **POST** `/api/socios/{id}/activar/` - Activar socio
- **POST** `/api/socios/{id}/desactivar/` - Desactivar socio
- **GET** `/api/socios/{id}/parcelas/` - Obtener parcelas del socio
- **GET** `/api/socios/{id}/cultivos/` - Obtener cultivos del socio

### UsuarioViewSet
- **POST** `/api/usuarios/{id}/activar/` - Activar usuario
- **POST** `/api/usuarios/{id}/desactivar/` - Desactivar usuario
- **GET** `/api/usuarios/{id}/roles/` - Obtener roles del usuario

## Consideraciones de Rendimiento - CU3

### Optimizaciones Implementadas:
- **Select Related:** Carga relacionada de usuario, comunidad, parcela, cultivo
- **Paginación:** Resultados paginados para listas grandes
- **Índices:** Campos de búsqueda indexados en base de datos
- **Filtros Eficientes:** Filtros a nivel de base de datos
- **Cache:** Resultados de reportes cacheados cuando apropiado

### Recomendaciones de Uso:
```javascript
// Búsqueda eficiente con paginación
const buscarSociosPaginado = async (filtros, page = 1) => {
  const params = new URLSearchParams({
    ...filtros,
    page: page.toString(),
    page_size: '20'
  });
  
  return await fetch(`/api/socios/buscar-avanzado/?${params}`);
};

// Validación en tiempo real
const validarCampo = async (campo, valor) => {
  const params = new URLSearchParams({ [campo]: valor });
  const response = await fetch(`/api/validar/datos-socio/?${params}`);
  const data = await response.json();
  
  if (!data.valido && data.errores[campo]) {
    return data.errores[campo];
  }
  
  return null;
};
```

## Migraciones de Base de Datos - CU3

Para implementar CU3, ejecutar las siguientes migraciones:

```bash
# Crear migraciones para nuevos campos y validaciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario si no existe
python manage.py createsuperuser
```

## Próximos Pasos

Con CU3 implementado, el sistema tiene una base sólida para:

1. **CU4:** Gestión avanzada de parcelas y cultivos
2. **CU5:** Sistema de reportes y estadísticas
3. **CU6:** Gestión de productos y comercialización
4. **CU7:** Sistema de pagos y facturación
5. **CU8:** Integración con sistemas externos

Cada CU siguiente puede aprovechar la arquitectura y patrones establecidos en CU1, CU2 y CU3.

### CU4: Gestión Avanzada de Parcelas y Cultivos
**Descripción:**  
El Caso de Uso CU4 implementa la gestión avanzada de parcelas y cultivos en el sistema de cooperativa agrícola. Incluye ciclos completos de cultivo, registro de cosechas, tratamientos aplicados, análisis de suelo y transferencias de parcelas entre socios. Este CU es fundamental para el seguimiento detallado de la producción agrícola y la toma de decisiones informadas.

**Objetivos:**
- Gestionar ciclos completos de cultivo desde siembra hasta cosecha
- Registrar cosechas con detalles de calidad y rendimiento
- Controlar tratamientos aplicados (fertilizantes, pesticidas, etc.)
- Realizar análisis de suelo para optimizar producción
- Gestionar transferencias de parcelas entre socios
- Generar reportes de productividad y rendimiento
- Mantener auditoría completa de todas las operaciones agrícolas
- Validar datos técnicos y restricciones de negocio

**Actores:**
- Socio agricultor (gestión de sus parcelas y cultivos)
- Administrador del sistema
- Técnico agrícola
- Sistema de validación de datos agrícolas

**Precondiciones:**
- Usuario debe estar autenticado
- Parcelas deben existir y estar activas
- Socios deben estar activos para transferencias
- Datos de cultivos deben ser consistentes

**Flujo Principal - Gestión de Ciclos de Cultivo:**
1. Usuario selecciona parcela y cultivo
2. Sistema valida permisos y estado de parcela
3. Usuario define ciclo (fechas, costos estimados, rendimientos esperados)
4. Sistema crea ciclo de cultivo con estado PLANIFICADO
5. Usuario puede actualizar estado del ciclo (SIEMBRA, CRECIMIENTO, COSECHA, FINALIZADO)
6. Sistema registra cambios en bitácora de auditoría
7. Sistema calcula progreso y métricas del ciclo

**Flujo Principal - Registro de Cosechas:**
1. Usuario selecciona ciclo de cultivo en estado COSECHA
2. Usuario registra datos de cosecha (cantidad, calidad, precio)
3. Sistema valida datos técnicos y consistencia
4. Sistema calcula valor total y rendimiento real
5. Sistema actualiza ciclo con rendimiento real
6. Sistema registra cosecha en bitácora

**Flujo Principal - Tratamientos:**
1. Usuario selecciona ciclo de cultivo activo
2. Usuario registra tratamiento (tipo, producto, dosis, fecha)
3. Sistema valida compatibilidad con cultivo y fechas
4. Sistema registra costo y aplicación
5. Sistema actualiza bitácora con detalles del tratamiento

**Flujo Principal - Análisis de Suelo:**
1. Usuario selecciona parcela
2. Usuario registra análisis (pH, nutrientes, laboratorio)
3. Sistema valida rangos técnicos
4. Sistema genera recomendaciones automáticas
5. Sistema registra análisis en bitácora

**Flujo Principal - Transferencias de Parcelas:**
1. Usuario solicita transferencia de parcela
2. Sistema valida propietario actual y socio nuevo
3. Sistema verifica no haber transferencias pendientes
4. Administrador aprueba o rechaza transferencia
5. Sistema actualiza propietario de parcela
6. Sistema registra transferencia en bitácora

**Flujos Alternativos:**
- **Parcela Inactiva:** Error con mensaje específico
- **Permisos Insuficientes:** Denegación con detalles
- **Datos Técnicos Inválidos:** Validaciones específicas por campo
- **Fechas Inconsistentes:** Verificación de lógica temporal
- **Transferencia Duplicada:** Prevención de transferencias múltiples

**Postcondiciones:**
- Ciclos de cultivo creados con seguimiento completo
- Cosechas registradas con métricas de rendimiento
- Tratamientos documentados con costos
- Análisis de suelo con recomendaciones
- Transferencias procesadas con auditoría
- Reportes de productividad generados
- Bitácora de auditoría actualizada

**Guía de Implementación - CU4:**

#### Para Frontend Web (React):
```javascript
// Servicio de gestión agrícola
class GestionAgricolaService {
  static baseUrl = '/api';

  // Ciclos de Cultivo
  static async crearCicloCultivo(cicloData) {
    try {
      const response = await fetch(`${this.baseUrl}/ciclo-cultivos/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cicloData)
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Ciclo creado:', data);
        return { success: true, data };
      } else {
        console.error('Error al crear ciclo:', data);
        return { success: false, errors: data };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Registrar Cosecha
  static async registrarCosecha(cosechaData) {
    try {
      const response = await fetch(`${this.baseUrl}/cosechas/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cosechaData)
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Cosecha registrada:', data);
        return { success: true, data };
      } else {
        console.error('Error al registrar cosecha:', data);
        return { success: false, errors: data };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Aplicar Tratamiento
  static async aplicarTratamiento(tratamientoData) {
    try {
      const response = await fetch(`${this.baseUrl}/tratamientos/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tratamientoData)
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Tratamiento aplicado:', data);
        return { success: true, data };
      } else {
        console.error('Error al aplicar tratamiento:', data);
        return { success: false, errors: data };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Registrar Análisis de Suelo
  static async registrarAnalisisSuelo(analisisData) {
    try {
      const response = await fetch(`${this.baseUrl}/analisis-suelo/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analisisData)
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Análisis registrado:', data);
        return { success: true, data };
      } else {
        console.error('Error al registrar análisis:', data);
        return { success: false, errors: data };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Solicitar Transferencia de Parcela
  static async solicitarTransferenciaParcela(transferenciaData) {
    try {
      const response = await fetch(`${this.baseUrl}/transferencias-parcela/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transferenciaData)
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Transferencia solicitada:', data);
        return { success: true, data };
      } else {
        console.error('Error al solicitar transferencia:', data);
        return { success: false, errors: data };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Procesar Transferencia (Admin)
  static async procesarTransferencia(transferenciaId, accion, observaciones = '') {
    try {
      const response = await fetch(`${this.baseUrl}/transferencias-parcela/${transferenciaId}/procesar/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          accion: accion,
          observaciones: observaciones
        })
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Transferencia procesada:', data);
        return { success: true, data };
      } else {
        console.error('Error al procesar transferencia:', data);
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Búsqueda Avanzada de Ciclos
  static async buscarCiclosCultivo(filtros = {}) {
    try {
      const params = new URLSearchParams();
      
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params.append(key, value);
        }
      });

      const response = await fetch(`${this.baseUrl}/ciclo-cultivos/buscar-avanzado/?${params}`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  // Validar Transferencia
  static async validarTransferencia(parcelaId, socioNuevoId) {
    try {
      const params = new URLSearchParams({
        parcela_id: parcelaId,
        socio_nuevo_id: socioNuevoId
      });

      const response = await fetch(`${this.baseUrl}/validar/transferencia-parcela/?${params}`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        return { valido: data.valido, mensaje: data.mensaje, errores: data.errores };
      } else {
        return { valido: false, errores: data.errores };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { valido: false, error: 'Error de conexión' };
    }
  }

  // Obtener Reportes de Productividad
  static async obtenerReporteProductividad() {
    try {
      const response = await fetch(`${this.baseUrl}/reportes/productividad-parcelas/`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }
}

// Componente de Gestión de Ciclos de Cultivo
class GestionCiclosCultivo extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ciclos: [],
      filtros: {
        especie: '',
        estado_ciclo: '',
        comunidad_id: '',
        fecha_inicio_desde: '',
        fecha_inicio_hasta: ''
      },
      loading: false,
      error: null
    };
  }

  componentDidMount() {
    this.cargarCiclos();
  }

  async cargarCiclos() {
    this.setState({ loading: true, error: null });
    
    const result = await GestionAgricolaService.buscarCiclosCultivo(this.state.filtros);
    
    if (result.success) {
      this.setState({ 
        ciclos: result.data.results,
        loading: false 
      });
    } else {
      this.setState({ 
        error: result.error,
        loading: false 
      });
    }
  }

  handleFiltroChange = (campo, valor) => {
    this.setState(prevState => ({
      filtros: {
        ...prevState.filtros,
        [campo]: valor
      }
    }));
  }

  handleBuscar = () => {
    this.cargarCiclos();
  }

  handleCrearCiclo = async (cicloData) => {
    const result = await GestionAgricolaService.crearCicloCultivo(cicloData);
    
    if (result.success) {
      alert('Ciclo de cultivo creado exitosamente');
      this.cargarCiclos();
    } else {
      alert(`Error: ${JSON.stringify(result.errors)}`);
    }
  }

  render() {
    const { ciclos, filtros, loading, error } = this.state;

    return (
      <div className="gestion-ciclos">
        <h2>Gestión de Ciclos de Cultivo</h2>
        
        {/* Filtros */}
        <div className="filtros">
          <input
            type="text"
            placeholder="Especie"
            value={filtros.especie}
            onChange={(e) => this.handleFiltroChange('especie', e.target.value)}
          />
          <select
            value={filtros.estado_ciclo}
            onChange={(e) => this.handleFiltroChange('estado_ciclo', e.target.value)}
          >
            <option value="">Todos los estados</option>
            <option value="PLANIFICADO">Planificado</option>
            <option value="SIEMBRA">En Siembra</option>
            <option value="CRECIMIENTO">En Crecimiento</option>
            <option value="COSECHA">En Cosecha</option>
            <option value="FINALIZADO">Finalizado</option>
          </select>
          <input
            type="date"
            placeholder="Fecha inicio desde"
            value={filtros.fecha_inicio_desde}
            onChange={(e) => this.handleFiltroChange('fecha_inicio_desde', e.target.value)}
          />
          <input
            type="date"
            placeholder="Fecha inicio hasta"
            value={filtros.fecha_inicio_hasta}
            onChange={(e) => this.handleFiltroChange('fecha_inicio_hasta', e.target.value)}
          />
          <button onClick={this.handleBuscar} disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>

        {/* Lista de Ciclos */}
        {error && <div className="error">{error}</div>}
        
        <div className="ciclos-list">
          {ciclos.map(ciclo => (
            <div key={ciclo.id} className="ciclo-card">
              <div className="ciclo-info">
                <h3>{ciclo.cultivo.especie} - {ciclo.parcela.nombre}</h3>
                <p>Estado: {ciclo.estado}</p>
                <p>Fecha Inicio: {ciclo.fecha_inicio}</p>
                <p>Fecha Fin Estimada: {ciclo.fecha_estimada_fin}</p>
                <p>Rendimiento Esperado: {ciclo.rendimiento_esperado} {ciclo.unidad_rendimiento}</p>
                <p>Costo Estimado: Bs. {ciclo.costo_estimado}</p>
              </div>
              <div className="ciclo-actions">
                <button onClick={() => this.handleEditarCiclo(ciclo.id)}>
                  Editar
                </button>
                <button onClick={() => this.handleVerCosechas(ciclo.id)}>
                  Ver Cosechas
                </button>
                <button onClick={() => this.handleVerTratamientos(ciclo.id)}>
                  Ver Tratamientos
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
}
```

#### Para Aplicación Móvil (Flutter) - CU4:
```dart
// Servicio de gestión agrícola
class GestionAgricolaService {
  static const String baseUrl = 'http://localhost:8000/api';

  // Crear ciclo de cultivo
  static Future<Map<String, dynamic>> crearCicloCultivo(Map<String, dynamic> cicloData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/ciclo-cultivos/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode(cicloData),
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Registrar cosecha
  static Future<Map<String, dynamic>> registrarCosecha(Map<String, dynamic> cosechaData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/cosechas/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode(cosechaData),
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Aplicar tratamiento
  static Future<Map<String, dynamic>> aplicarTratamiento(Map<String, dynamic> tratamientoData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/tratamientos/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode(tratamientoData),
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Registrar análisis de suelo
  static Future<Map<String, dynamic>> registrarAnalisisSuelo(Map<String, dynamic> analisisData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/analisis-suelo/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode(analisisData),
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Solicitar transferencia
  static Future<Map<String, dynamic>> solicitarTransferenciaParcela(Map<String, dynamic> transferenciaData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/transferencias-parcela/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode(transferenciaData),
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Procesar transferencia (Admin)
  static Future<Map<String, dynamic>> procesarTransferencia(int transferenciaId, String accion, String observaciones) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.post(
        Uri.parse('$baseUrl/transferencias-parcela/$transferenciaId/procesar/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({
          'accion': accion,
          'observaciones': observaciones
        }),
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Búsqueda avanzada de ciclos
  static Future<Map<String, dynamic>> buscarCiclosCultivo(Map<String, String> filtros) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final params = filtros.entries
        .where((entry) => entry.value.isNotEmpty)
        .map((entry) => '${entry.key}=${Uri.encodeComponent(entry.value)}')
        .join('&');
      
      final response = await http.get(
        Uri.parse('$baseUrl/ciclo-cultivos/buscar-avanzado/?$params'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Validar transferencia
  static Future<Map<String, dynamic>> validarTransferencia(int parcelaId, int socioNuevoId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.get(
        Uri.parse('$baseUrl/validar/transferencia-parcela/?parcela_id=$parcelaId&socio_nuevo_id=$socioNuevoId'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // Obtener reporte de productividad
  static Future<Map<String, dynamic>> obtenerReporteProductividad() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('csrf_token');
      
      final response = await http.get(
        Uri.parse('$baseUrl/reportes/productividad-parcelas/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json'
        },
      );

      return jsonDecode(response.body);
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }
}

// Widget de Gestión de Ciclos de Cultivo
class GestionCiclosScreen extends StatefulWidget {
  @override
  _GestionCiclosScreenState createState() => _GestionCiclosScreenState();
}

class _GestionCiclosScreenState extends State<GestionCiclosScreen> {
  List<dynamic> _ciclos = [];
  Map<String, String> _filtros = {
    'especie': '',
    'estado_ciclo': '',
    'fecha_inicio_desde': '',
    'fecha_inicio_hasta': '',
  };
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _cargarCiclos();
  }

  Future<void> _cargarCiclos() async {
    setState(() => _isLoading = true);

    final result = await GestionAgricolaService.buscarCiclosCultivo(_filtros);

    setState(() => _isLoading = false);

    if (result.containsKey('results')) {
      setState(() {
        _ciclos = result['results'];
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${result['error']}'))
      );
    }
  }

  Future<void> _crearCiclo() async {
    // Navegar a pantalla de crear ciclo
    final result = await Navigator.pushNamed(context, '/crear-ciclo');
    
    if (result == true) {
      _cargarCiclos(); // Recargar lista
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Ciclos de Cultivo'),
        actions: [
          IconButton(
            icon: Icon(Icons.search),
            onPressed: _cargarCiclos,
          ),
        ],
      ),
      body: Column(
        children: [
          // Filtros
          Padding(
            padding: EdgeInsets.all(8.0),
            child: Column(
              children: [
                TextField(
                  decoration: InputDecoration(
                    labelText: 'Especie',
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (value) => _filtros['especie'] = value,
                ),
                SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  decoration: InputDecoration(
                    labelText: 'Estado',
                    border: OutlineInputBorder(),
                  ),
                  value: _filtros['estado_ciclo'],
                  items: [
                    DropdownMenuItem(value: '', child: Text('Todos')),
                    DropdownMenuItem(value: 'PLANIFICADO', child: Text('Planificado')),
                    DropdownMenuItem(value: 'SIEMBRA', child: Text('En Siembra')),
                    DropdownMenuItem(value: 'CRECIMIENTO', child: Text('En Crecimiento')),
                    DropdownMenuItem(value: 'COSECHA', child: Text('En Cosecha')),
                    DropdownMenuItem(value: 'FINALIZADO', child: Text('Finalizado')),
                  ],
                  onChanged: (value) => setState(() => _filtros['estado_ciclo'] = value ?? ''),
                ),
                SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          labelText: 'Fecha inicio desde',
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (value) => _filtros['fecha_inicio_desde'] = value,
                      ),
                    ),
                    SizedBox(width: 8),
                    Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          labelText: 'Fecha inicio hasta',
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (value) => _filtros['fecha_inicio_hasta'] = value,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Lista de Ciclos
          Expanded(
            child: _isLoading
              ? Center(child: CircularProgressIndicator())
              : ListView.builder(
                  itemCount: _ciclos.length,
                  itemBuilder: (context, index) {
                    final ciclo = _ciclos[index];
                    return Card(
                      margin: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${ciclo['cultivo']['especie']} - ${ciclo['parcela']['nombre']}',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            Text('Estado: ${ciclo['estado']}'),
                            Text('Fecha Inicio: ${ciclo['fecha_inicio']}'),
                            Text('Fecha Fin Estimada: ${ciclo['fecha_estimada_fin']}'),
                            Text('Rendimiento Esperado: ${ciclo['rendimiento_esperado']} ${ciclo['unidad_rendimiento']}'),
                            Text('Costo Estimado: Bs. ${ciclo['costo_estimado']}'),
                            SizedBox(height: 8),
                            Row(
                              children: [
                                Expanded(
                                  child: ElevatedButton(
                                    onPressed: () {
                                      // Navegar a editar ciclo
                                      Navigator.pushNamed(context, '/editar-ciclo', arguments: ciclo['id']);
                                    },
                                    child: Text('Editar'),
                                  ),
                                ),
                                SizedBox(width: 8),
                                Expanded(
                                  child: ElevatedButton(
                                    onPressed: () {
                                      // Navegar a cosechas del ciclo
                                      Navigator.pushNamed(context, '/cosechas-ciclo', arguments: ciclo['id']);
                                    },
                                    child: Text('Cosechas'),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _crearCiclo,
        child: Icon(Icons.add),
        tooltip: 'Crear Ciclo',
      ),
    );
  }
}
```

**Consideraciones de Seguridad para CU4:**
- Todas las operaciones requieren autenticación y permisos adecuados
- Los socios solo pueden gestionar sus propias parcelas y cultivos
- Los administradores pueden gestionar todas las parcelas
- Se registra cada operación en bitácora de auditoría con detalles técnicos
- Validaciones de datos técnicos previenen errores en producción
- Control de acceso basado en roles para operaciones administrativas

**Validaciones Técnicas Implementadas en CU4:**
- **Fechas:** Lógica temporal (inicio < fin, fechas no pasadas para siembra)
- **Superficies:** Consistencia entre parcela y hectáreas sembradas
- **Dosis:** Rangos seguros para tratamientos agrícolas
- **pH del Suelo:** Valores realistas entre 0-14
- **Rendimientos:** Valores positivos y consistentes con especie
- **Coordenadas:** Validación geográfica de ubicación
- **Transferencias:** Prevención de transferencias duplicadas o inválidas

**Manejo de Errores en CU4:**
- **Datos Técnicos Inválidos:** Mensajes específicos por campo agrícola
- **Permisos Insuficientes:** Error 403 con contexto claro
- **Recursos No Encontrados:** Error 404 con detalles específicos
- **Inconsistencias de Datos:** Validaciones de negocio específicas
- **Errores de Conexión:** Reintento automático con retroceso
- **Estados Inválidos:** Transiciones de estado controladas

**Pruebas Recomendadas para CU4:**
1. Crear ciclo de cultivo con datos válidos
2. Crear ciclo con fechas inválidas (verificar validaciones)
3. Registrar cosecha completa con cálculos automáticos
4. Aplicar tratamiento con dosis y costos
5. Registrar análisis de suelo con recomendaciones
6. Solicitar y procesar transferencia de parcela
7. Búsqueda avanzada de ciclos con múltiples filtros
8. Generar reportes de productividad
9. Validar transferencias antes de procesar
10. Verificar registros en bitácora de auditoría
11. Probar permisos insuficientes en operaciones
12. Validar límites técnicos (superficies, dosis, pH)

## Endpoints Adicionales - CU4

### Gestión de Ciclos de Cultivo

#### GET /api/ciclo-cultivos/buscar-avanzado/
Búsqueda avanzada de ciclos de cultivo con filtros múltiples.

**Parámetros de Query:**
- `especie`: Filtrar por especie del cultivo
- `estado_ciclo`: Estado del ciclo (PLANIFICADO, SIEMBRA, etc.)
- `comunidad_id`: ID de comunidad
- `fecha_inicio_desde`: Fecha inicio desde
- `fecha_inicio_hasta`: Fecha inicio hasta
- `page`: Página (paginación)
- `page_size`: Tamaño de página

**Response:**
```json
{
    "count": 25,
    "page": 1,
    "page_size": 20,
    "total_pages": 2,
    "filtros": {
        "especie": "Maíz",
        "estado_ciclo": "CRECIMIENTO",
        "comunidad_id": "1",
        "fecha_inicio_desde": "2024-01-01",
        "fecha_inicio_hasta": "2024-12-31"
    },
    "results": [...]
}
```

### Gestión de Cosechas

#### POST /api/cosechas/
Registrar nueva cosecha.

**Request Body:**
```json
{
    "ciclo_cultivo": 1,
    "fecha_cosecha": "2024-05-15",
    "cantidad_cosechada": 8000.50,
    "unidad_medida": "kg",
    "calidad": "BUENA",
    "precio_venta": 2.75,
    "observaciones": "Cosecha excelente, buen rendimiento"
}
```

**Response:**
```json
{
    "id": 1,
    "ciclo_cultivo": 1,
    "fecha_cosecha": "2024-05-15",
    "cantidad_cosechada": 8000.50,
    "unidad_medida": "kg",
    "calidad": "BUENA",
    "precio_venta": 2.75,
    "valor_total": 22006.375,
    "observaciones": "Cosecha excelente, buen rendimiento",
    "creado_en": "2024-05-15T10:00:00Z"
}
```

### Gestión de Tratamientos

#### POST /api/tratamientos/
Aplicar tratamiento a un ciclo de cultivo.

**Request Body:**
```json
{
    "ciclo_cultivo": 1,
    "tipo_tratamiento": "FERTILIZANTE",
    "nombre_producto": "Urea 46-0-0",
    "dosis": 250.00,
    "unidad_dosis": "kg/ha",
    "fecha_aplicacion": "2024-02-20",
    "costo": 1875.00,
    "aplicado_por": "Juan Pérez",
    "observaciones": "Aplicación preventiva de nitrógeno"
}
```

**Response:**
```json
{
    "id": 1,
    "ciclo_cultivo": 1,
    "tipo_tratamiento": "FERTILIZANTE",
    "nombre_producto": "Urea 46-0-0",
    "dosis": 250.00,
    "unidad_dosis": "kg/ha",
    "fecha_aplicacion": "2024-02-20",
    "costo": 1875.00,
    "aplicado_por": "Juan Pérez",
    "observaciones": "Aplicación preventiva de nitrógeno",
    "creado_en": "2024-02-20T08:00:00Z"
}
```

### Gestión de Análisis de Suelo

#### POST /api/analisis-suelo/
Registrar análisis de suelo.

**Request Body:**
```json
{
    "parcela": 1,
    "fecha_analisis": "2024-01-15",
    "ph": 6.8,
    "materia_organica": 3.5,
    "nitrogeno": 0.18,
    "fosforo": 32.0,
    "potasio": 220.0,
    "laboratorio": "Laboratorio Agroquímico ABC",
    "recomendaciones": "Suelo en buenas condiciones, mantener fertilización balanceada",
    "costo_analisis": 650.00
}
```

**Response:**
```json
{
    "id": 1,
    "parcela": 1,
    "fecha_analisis": "2024-01-15",
    "ph": 6.8,
    "materia_organica": 3.5,
    "nitrogeno": 0.18,
    "fosforo": 32.0,
    "potasio": 220.0,
    "laboratorio": "Laboratorio Agroquímico ABC",
    "recomendaciones": "Suelo en buenas condiciones, mantener fertilización balanceada",
    "costo_analisis": 650.00,
    "recomendaciones_basicas": [
        "pH en rango óptimo",
        "Nitrógeno en niveles adecuados",
        "Fósforo en niveles adecuados",
        "Potasio en niveles adecuados"
    ],
    "creado_en": "2024-01-15T09:00:00Z"
}
```

### Gestión de Transferencias de Parcela

#### POST /api/transferencias-parcela/
Solicitar transferencia de parcela.

**Request Body:**
```json
{
    "parcela": 1,
    "socio_anterior": 1,
    "socio_nuevo": 2,
    "fecha_transferencia": "2024-06-01",
    "motivo": "Venta de parcela por jubilación",
    "documento_legal": "Contrato de compraventa No. 2024-001",
    "costo_transferencia": 5000.00,
    "observaciones": "Transferencia acordada entre las partes"
}
```

**Response:**
```json
{
    "id": 1,
    "parcela": 1,
    "socio_anterior": 1,
    "socio_nuevo": 2,
    "fecha_transferencia": "2024-06-01",
    "motivo": "Venta de parcela por jubilación",
    "documento_legal": "Contrato de compraventa No. 2024-001",
    "costo_transferencia": 5000.00,
    "estado": "PENDIENTE",
    "observaciones": "Transferencia acordada entre las partes",
    "creado_en": "2024-05-20T14:00:00Z"
}
```

#### POST /api/transferencias-parcela/{id}/procesar/
Procesar transferencia (aprobar/rechazar) - Solo administradores.

**Request Body:**
```json
{
    "accion": "APROBAR",
    "observaciones": "Transferencia aprobada, documentación completa"
}
```

**Response:**
```json
{
    "mensaje": "Transferencia aprobada exitosamente",
    "transferencia": {
        "id": 1,
        "estado": "APROBADA",
        "fecha_aprobacion": "2024-05-25T10:00:00Z",
        "aprobado_por": 3,
        "observaciones": "Transferencia aprobada, documentación completa"
    }
}
```

### Validación de Datos

#### GET /api/validar/transferencia-parcela/
Validar transferencia antes de procesar.

**Parámetros de Query:**
- `parcela_id`: ID de la parcela
- `socio_nuevo_id`: ID del socio nuevo

**Response (válido):**
```json
{
    "valido": true,
    "mensaje": "La transferencia puede proceder",
    "detalles": {
        "parcela": "Parcela Central",
        "socio_actual": "123456789 - Juan Pérez López",
        "socio_nuevo": "987654321 - María González Ruiz"
    }
}
```

**Response (inválido):**
```json
{
    "valido": false,
    "errores": [
        "El socio nuevo debe estar activo",
        "Ya existe una transferencia pendiente para esta parcela"
    ]
}
```

### Reportes

#### GET /api/reportes/productividad-parcelas/
Obtener reporte de productividad de parcelas - Solo administradores.

**Response:**
```json
{
    "estadisticas_generales": {
        "cosechas_total": 45,
        "cosechas_completadas": 42,
        "cosechas_pendientes": 3,
        "porcentaje_completadas": 93.33
    },
    "productividad_por_especie": [
        {
            "especie": "Maíz",
            "total_cosechado": 125000.50,
            "num_ciclos": 15,
            "num_cosechas": 28
        },
        {
            "especie": "Soya",
            "total_cosechado": 87500.25,
            "num_ciclos": 12,
            "num_cosechas": 17
        }
    ],
    "rendimiento_parcelas_top20": [
        {
            "nombre": "Parcela 5",
            "superficie_total": 25.0,
            "total_cosechado": 50000.00,
            "rendimiento_promedio": 2000.0
        }
    ],
    "tratamientos_por_mes": [
        {
            "mes": "2024-03-01",
            "tipo_tratamiento": "FERTILIZANTE",
            "count": 12
        }
    ],
    "analisis_suelo_por_tipo": [
        {
            "tipo_analisis": "Completo",
            "count": 8,
            "promedio_ph": 6.45,
            "promedio_materia_organica": 3.2
        }
    ]
}
```

## Acciones en ViewSets - CU4

### CicloCultivoViewSet
- **GET** `/api/ciclo-cultivos/` - Lista ciclos de cultivo
- **POST** `/api/ciclo-cultivos/` - Crear ciclo de cultivo
- **GET** `/api/ciclo-cultivos/{id}/` - Obtener ciclo específico
- **PUT** `/api/ciclo-cultivos/{id}/` - Actualizar ciclo
- **DELETE** `/api/ciclo-cultivos/{id}/` - Eliminar ciclo

### CosechaViewSet
- **GET** `/api/cosechas/` - Lista cosechas
- **POST** `/api/cosechas/` - Registrar cosecha
- **GET** `/api/cosechas/{id}/` - Obtener cosecha específica
- **PUT** `/api/cosechas/{id}/` - Actualizar cosecha
- **DELETE** `/api/cosechas/{id}/` - Eliminar cosecha

### TratamientoViewSet
- **GET** `/api/tratamientos/` - Lista tratamientos
- **POST** `/api/tratamientos/` - Aplicar tratamiento
- **GET** `/api/tratamientos/{id}/` - Obtener tratamiento específico
- **PUT** `/api/tratamientos/{id}/` - Actualizar tratamiento
- **DELETE** `/api/tratamientos/{id}/` - Eliminar tratamiento

### AnalisisSueloViewSet
- **GET** `/api/analisis-suelo/` - Lista análisis de suelo
- **POST** `/api/analisis-suelo/` - Registrar análisis
- **GET** `/api/analisis-suelo/{id}/` - Obtener análisis específico
- **PUT** `/api/analisis-suelo/{id}/` - Actualizar análisis
- **DELETE** `/api/analisis-suelo/` - Eliminar análisis

### TransferenciaParcelaViewSet
- **GET** `/api/transferencias-parcela/` - Lista transferencias
- **POST** `/api/transferencias-parcela/` - Solicitar transferencia
- **GET** `/api/transferencias-parcela/{id}/` - Obtener transferencia específica
- **PUT** `/api/transferencias-parcela/{id}/` - Actualizar transferencia
- **DELETE** `/api/transferencias-parcela/{id}/` - Eliminar transferencia

## Consideraciones de Rendimiento - CU4

### Optimizaciones Implementadas:
- **Select Related:** Carga relacionada de parcela, cultivo, socio, comunidad
- **Paginación:** Resultados paginados para listas grandes de ciclos/cosechas
- **Índices:** Campos de búsqueda indexados (fechas, especies, estados)
- **Filtros Eficientes:** Filtros a nivel de base de datos
- **Agregaciones:** Cálculos de productividad usando funciones de BD
- **Cache:** Resultados de reportes cacheados cuando apropiado

### Recomendaciones de Uso:
```javascript
// Búsqueda eficiente con filtros
const buscarCiclosAvanzado = async (filtros, page = 1) => {
  const params = new URLSearchParams({
    ...filtros,
    page: page.toString(),
    page_size: '20'
  });
  
  return await fetch(`/api/ciclo-cultivos/buscar-avanzado/?${params}`);
};

// Validación en tiempo real
const validarTransferencia = async (parcelaId, socioNuevoId) => {
  const params = new URLSearchParams({
    parcela_id: parcelaId,
    socio_nuevo_id: socioNuevoId
  });
  
  const response = await fetch(`/api/validar/transferencia-parcela/?${params}`);
  const data = await response.json();
  
  return {
    valido: data.valido,
    errores: data.errores || [],
    mensaje: data.mensaje
  };
};

// Monitoreo de progreso de ciclos
const obtenerProgresoCiclo = (ciclo) => {
  const hoy = new Date();
  const inicio = new Date(ciclo.fecha_inicio);
  const fin = new Date(ciclo.fecha_estimada_fin);
  
  const totalDias = (fin - inicio) / (1000 * 60 * 60 * 24);
  const diasTranscurridos = (hoy - inicio) / (1000 * 60 * 60 * 24);
  
  return Math.min(100, Math.max(0, (diasTranscurridos / totalDias) * 100));
};
```

## Migraciones de Base de Datos - CU4

Para implementar CU4, ejecutar las siguientes migraciones:

```bash
# Crear migraciones para nuevos modelos de CU4
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear datos de prueba (opcional)
python manage.py shell -c "
from cooperativa.models import *
# Crear ciclos, cosechas, tratamientos, análisis y transferencias de prueba
"
```

## CU6: Gestionar Roles y Permisos
**Descripción:**  
El Caso de Uso CU6 permite la gestión completa de roles y permisos en el sistema de cooperativa agrícola. Incluye operaciones de creación, modificación, eliminación de roles, asignación y remoción de roles a usuarios, validación de permisos, y funcionalidades avanzadas como duplicación de roles y reportes de permisos. Este CU es fundamental para el control de acceso y seguridad del sistema.

**Objetivos:**
- Gestionar el ciclo de vida completo de los roles (creación, modificación, eliminación)
- Administrar permisos granulares por módulo y acción
- Asignar y remover roles a usuarios de manera segura
- Validar permisos de usuarios en tiempo real
- Proporcionar herramientas avanzadas de gestión de roles
- Mantener auditoría completa de todas las operaciones de roles
- Gestionar roles del sistema con restricciones especiales
- Generar reportes sobre asignaciones de roles y permisos

**Actores:**
- Administrador del sistema
- Usuario con permisos de gestión de roles
- Sistema de validación de permisos

**Precondiciones:**
- Usuario debe estar autenticado y tener permisos de administrador
- Roles del sistema deben estar protegidos contra eliminación
- Operaciones críticas requieren confirmación adicional

**Flujo Principal - Gestión de Roles:**
1. Usuario solicita operación sobre roles (crear, editar, eliminar)
2. Sistema valida permisos del usuario para gestión de roles
3. Sistema aplica reglas específicas para roles del sistema
4. Usuario ingresa/modifica datos del rol y permisos
5. Sistema valida estructura de permisos y unicidad de nombre
6. Sistema registra operación en bitácora de auditoría
7. Sistema confirma operación exitosa

**Flujo Principal - Asignación de Roles:**
1. Usuario selecciona usuario y rol a asignar
2. Sistema valida que usuario tiene permisos para asignar roles
3. Sistema verifica que no existe asignación duplicada
4. Sistema crea relación usuario-rol
5. Sistema registra asignación en bitácora
6. Sistema confirma asignación exitosa

**Flujo Principal - Validación de Permisos:**
1. Sistema recibe solicitud de validación de permiso
2. Sistema identifica usuario y permiso requerido
3. Sistema consulta roles asignados al usuario
4. Sistema evalúa permisos consolidados del usuario
5. Sistema retorna resultado de validación

**Flujos Alternativos:**
- **Rol del Sistema:** Operaciones restringidas con mensaje específico
- **Permisos Insuficientes:** Operación denegada con mensaje claro
- **Duplicados Encontrados:** Sistema indica conflictos existentes
- **Datos Inválidos:** Validaciones específicas por campo
- **Usuario No Encontrado:** Error 404 con contexto específico

**Postcondiciones:**
- Roles y permisos actualizados correctamente
- Asignaciones usuario-rol sincronizadas
- Registros de auditoría creados con detalles completos
- Permisos del sistema consistentes y seguros

## Endpoints de CU6

### Gestión de Roles

#### GET /api/roles/
Lista todos los roles disponibles en el sistema.

**Parámetros de Query:**
- `page`: Página para paginación
- `page_size`: Número de elementos por página
- `search`: Búsqueda por nombre o descripción

**Response:**
```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "nombre": "ADMINISTRADOR",
            "descripcion": "Rol con permisos completos",
            "permisos": {
                "usuarios": {"ver": true, "crear": true, "editar": true, "eliminar": true, "aprobar": true},
                "socios": {"ver": true, "crear": true, "editar": true, "eliminar": true, "aprobar": true},
                "parcelas": {"ver": true, "crear": true, "editar": true, "eliminar": true, "aprobar": true},
                "cultivos": {"ver": true, "crear": true, "editar": true, "eliminar": true, "aprobar": true},
                "reportes": {"ver": true, "crear": true, "editar": true, "eliminar": true, "aprobar": true},
                "auditoria": {"ver": true, "crear": true, "editar": true, "eliminar": true, "aprobar": true}
            },
            "es_sistema": true,
            "creado_en": "2025-09-17T10:00:00Z",
            "actualizado_en": "2025-09-17T10:00:00Z"
        }
    ]
}
```

#### POST /api/roles/
Crea un nuevo rol personalizado.

**Request Body:**
```json
{
    "nombre": "ROL PERSONALIZADO",
    "descripcion": "Rol con permisos específicos",
    "permisos": {
        "usuarios": {"ver": true, "crear": false, "editar": false, "eliminar": false, "aprobar": false},
        "socios": {"ver": true, "crear": true, "editar": true, "eliminar": false, "aprobar": false},
        "parcelas": {"ver": true, "crear": true, "editar": true, "eliminar": false, "aprobar": false},
        "cultivos": {"ver": true, "crear": true, "editar": true, "eliminar": true, "aprobar": false},
        "reportes": {"ver": true, "crear": false, "editar": false, "eliminar": false, "aprobar": false},
        "auditoria": {"ver": false, "crear": false, "editar": false, "eliminar": false, "aprobar": false}
    }
}
```

**Response (éxito):**
```json
{
    "id": 5,
    "nombre": "ROL PERSONALIZADO",
    "descripcion": "Rol con permisos específicos",
    "permisos": {...},
    "es_sistema": false,
    "creado_en": "2025-09-17T11:00:00Z",
    "actualizado_en": "2025-09-17T11:00:00Z"
}
```

#### GET /api/roles/{id}/
Obtiene detalles de un rol específico.

**Response:**
```json
{
    "id": 1,
    "nombre": "ADMINISTRADOR",
    "descripcion": "Rol con permisos completos",
    "permisos": {...},
    "es_sistema": true,
    "creado_en": "2025-09-17T10:00:00Z",
    "actualizado_en": "2025-09-17T10:00:00Z"
}
```

#### PUT /api/roles/{id}/
Actualiza un rol existente.

**Request Body:**
```json
{
    "nombre": "ADMIN MODIFICADO",
    "descripcion": "Rol administrador modificado",
    "permisos": {...}
}
```

#### DELETE /api/roles/{id}/
Elimina un rol (no aplica a roles del sistema).

**Response (error para rol del sistema):**
```json
[
    {
        "string": "No se puede eliminar un rol del sistema",
        "code": "invalid"
    }
]
```

### Gestión de Asignaciones Usuario-Rol

#### POST /api/asignar-rol-usuario/
Asigna un rol a un usuario.

**Request Body:**
```json
{
    "usuario_id": 2,
    "rol_id": 3
}
```

**Response (éxito):**
```json
{
    "mensaje": "Rol asignado exitosamente",
    "usuario_rol": {
        "id": 10,
        "usuario": 2,
        "rol": 3,
        "asignado_en": "2025-09-17T11:00:00Z"
    }
}
```

**Response (error - rol ya asignado):**
```json
{
    "error": "El usuario ya tiene asignado este rol"
}
```

#### POST /api/quitar-rol-usuario/
Remueve un rol de un usuario.

**Request Body:**
```json
{
    "usuario_id": 2,
    "rol_id": 3
}
```

**Response (éxito):**
```json
{
    "mensaje": "Rol removido exitosamente"
}
```

**Response (error - último rol del sistema):**
```json
{
    "error": "No se puede remover el último rol del sistema de un usuario"
}
```

### Validación de Permisos

#### GET /api/validar-permiso-usuario/
Valida si un usuario tiene un permiso específico.

**Parámetros de Query:**
- `usuario_id`: ID del usuario (requerido)
- `modulo`: Módulo del permiso (requerido)
- `accion`: Acción del permiso (requerido)

**Ejemplo:** `/api/validar-permiso-usuario/?usuario_id=2&modulo=socios&accion=crear`

**Response:**
```json
{
    "usuario_id": 2,
    "modulo": "socios",
    "accion": "crear",
    "tiene_permiso": true
}
```

#### GET /api/permisos-usuario/{usuario_id}/
Obtiene todos los permisos consolidados de un usuario.

**Response:**
```json
{
    "usuario_id": 2,
    "usuario_info": {
        "nombres": "Juan",
        "apellidos": "Pérez",
        "usuario": "jperez"
    },
    "roles": [
        {
            "id": 2,
            "nombre": "SOCIO",
            "descripcion": "Rol para socios"
        }
    ],
    "permisos": {
        "usuarios": {"ver": false, "crear": false, "editar": false, "eliminar": false, "aprobar": false},
        "socios": {"ver": true, "crear": false, "editar": true, "eliminar": false, "aprobar": false},
        "parcelas": {"ver": true, "crear": true, "editar": true, "eliminar": false, "aprobar": false},
        "cultivos": {"ver": true, "crear": true, "editar": true, "eliminar": true, "aprobar": false},
        "reportes": {"ver": true, "crear": false, "editar": false, "eliminar": false, "aprobar": false},
        "auditoria": {"ver": false, "crear": false, "editar": false, "eliminar": false, "aprobar": false}
    }
}
```

### Operaciones Avanzadas de Roles

#### POST /api/roles/{id}/duplicar/
Duplica un rol existente con un nuevo nombre.

**Request Body:**
```json
{
    "nuevo_nombre": "SOCIO COPIA",
    "descripcion": "Copia del rol Socio"
}
```

**Response:**
```json
{
    "id": 6,
    "nombre": "SOCIO COPIA",
    "descripcion": "Copia del rol Socio",
    "permisos": {...},
    "es_sistema": false,
    "creado_en": "2025-09-17T11:30:00Z",
    "actualizado_en": "2025-09-17T11:30:00Z"
}
```

#### GET /api/roles/{id}/usuarios/
Obtiene todos los usuarios asignados a un rol específico.

**Response:**
```json
{
    "rol": {
        "id": 2,
        "nombre": "SOCIO",
        "descripcion": "Rol para socios"
    },
    "usuarios": [
        {
            "id": 2,
            "usuario": "jperez",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "estado": "ACTIVO",
            "asignado_en": "2025-09-17T10:00:00Z"
        }
    ]
}
```

#### GET /api/usuarios/{id}/roles/
Obtiene todos los roles asignados a un usuario específico.

**Response:**
```json
{
    "usuario": {
        "id": 2,
        "usuario": "jperez",
        "nombres": "Juan",
        "apellidos": "Pérez",
        "estado": "ACTIVO"
    },
    "roles": [
        {
            "id": 2,
            "nombre": "SOCIO",
            "descripcion": "Rol para socios",
            "asignado_en": "2025-09-17T10:00:00Z"
        }
    ]
}
```

## Estructura de Permisos

Los permisos en el sistema están organizados por módulos y acciones:

```json
{
    "usuarios": {
        "ver": true,
        "crear": true,
        "editar": true,
        "eliminar": true,
        "aprobar": true
    },
    "socios": {
        "ver": true,
        "crear": true,
        "editar": true,
        "eliminar": true,
        "aprobar": true
    },
    "parcelas": {
        "ver": true,
        "crear": true,
        "editar": true,
        "eliminar": true,
        "aprobar": true
    },
    "cultivos": {
        "ver": true,
        "crear": true,
        "editar": true,
        "eliminar": true,
        "aprobar": true
    },
    "reportes": {
        "ver": true,
        "crear": true,
        "editar": true,
        "eliminar": true,
        "aprobar": true
    },
    "auditoria": {
        "ver": true,
        "crear": true,
        "editar": true,
        "eliminar": true,
        "aprobar": true
    }
}
```

## Consideraciones de Seguridad para CU6

- **Roles del Sistema:** Los roles marcados como `es_sistema: true` no pueden ser eliminados
- **Permisos de Administrador:** Solo usuarios con rol administrador pueden gestionar roles
- **Auditoría Completa:** Todas las operaciones de roles se registran en bitácora
- **Validación de Unicidad:** Nombres de roles deben ser únicos en el sistema
- **Consistencia de Estados:** Estados de usuarios y roles se mantienen sincronizados
- **Protección contra Escalada:** Validaciones previenen asignación de permisos excesivos

## Manejo de Errores en CU6

- **401 Unauthorized:** Usuario no autenticado
- **403 Forbidden:** Usuario sin permisos para gestión de roles
- **404 Not Found:** Rol o usuario no encontrado
- **400 Bad Request:** Datos inválidos o reglas de negocio violadas
- **409 Conflict:** Intento de crear rol con nombre duplicado

## Próximos Pasos

Con CU6 implementado, el sistema tiene un control de acceso completo para:

1. **CU7:** Sistema avanzado de reportes y estadísticas
2. **CU8:** Gestión de productos y comercialización
3. **CU9:** Sistema de pagos y facturación
4. **CU10:** Integración con sistemas externos
5. **CU11:** Módulo de capacitación y asistencia técnica
6. **CU12:** Sistema de alertas y notificaciones

Cada CU siguiente puede aprovechar la arquitectura y patrones establecidos en CU1-CU6, incluyendo:
- Autenticación y sesiones seguras
- Gestión completa de usuarios, roles y permisos
- Validaciones robustas de datos
- Auditoría completa de operaciones
- APIs RESTful bien documentadas
- Manejo eficiente de datos agrícolas
- Reportes y análisis de productividad
- Interfaces optimizadas para web y móvil
- Control granular de acceso y seguridad