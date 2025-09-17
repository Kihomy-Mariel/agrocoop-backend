# 📚 Documentación del Sistema de Gestión Cooperativa Agrícola

## 📋 Índice General

Esta documentación está organizada por **Casos de Uso (CU)** implementados en el sistema. Cada CU contiene documentación detallada de sus tareas específicas, implementación técnica, endpoints API, validaciones y ejemplos de uso.

## 🗂️ Estructura de Documentación

```
docs/
├── README.md                           # Este archivo (índice general)
├── API_Documentation.md               # Documentación completa de API
├── IMPLEMENTATION_SUMMARY.md          # Resumen ejecutivo del proyecto
│
├── CU1_Autenticacion/
│   ├── README.md                      # Documentación completa CU1
│   ├── T011_Autenticacion_Sesiones.md # Gestión de autenticación
│   ├── T013_Bitacora_Basica.md        # Bitácora básica
│   ├── T020_Interfaces_Login.md       # Diseño de interfaces
│   ├── T023_Cierre_Sesion.md          # Implementación logout
│   └── T026_Vistas_Moviles.md         # Vistas móviles
│
├── CU2_Logout_Sesion/
│   ├── README.md                      # Documentación completa CU2
│   ├── T011_Autenticacion_Sesiones.md # Gestión de sesiones
│   ├── T023_Cierre_Sesion.md          # Logout web/móvil
│   └── T030_Bitacora_Extendida.md     # Bitácora extendida
│
├── CU3_Gestion_Socios/
│   ├── README.md                      # Documentación completa CU3
│   ├── T012_Gestion_Usuarios_Roles.md # Gestión usuarios/roles
│   ├── T014_CRUD_Socios.md            # CRUD de socios
│   ├── T016_Busquedas_Filtros.md      # Búsquedas y filtros
│   ├── T021_Validacion_Formularios.md # Validaciones
│   ├── T024_Vistas_Usuarios_Roles.md  # Interfaces web
│   ├── T025_Vistas_Socios_Parcelas.md # Interfaces web
│   ├── T027_Validacion_Duplicados.md  # Validación duplicados
│   ├── T029_Busqueda_Avanzada.md      # Búsqueda avanzada
│   └── T031_Reportes_Usuarios.md      # Reportes usuarios
│
├── CU4_Gestion_Parcelas/
│   ├── README.md                      # Documentación completa CU4
│   ├── T015_Registro_Parcelas.md      # Registro de parcelas
│   ├── T021_Validacion_Datos.md       # Validaciones
│   ├── T025_Vistas_Parcelas.md        # Interfaces web
│   └── T034_Documentacion_Tecnica.md  # Documentación técnica
│
├── CU5_Consultas_Filtros/
│   ├── README.md                      # Documentación completa CU5
│   ├── T016_Busquedas_Filtros.md      # Búsquedas y filtros
│   ├── T026_Vistas_Moviles.md         # Vistas móviles
│   ├── T029_Busqueda_Avanzada.md      # Búsqueda avanzada
│   └── T031_Reportes_Basicos.md       # Reportes básicos
│
└── CU6_Roles_Permisos/
    ├── README.md                      # Documentación completa CU6
    ├── T012_Gestion_Usuarios_Roles.md # Gestión usuarios/roles
    ├── T022_Configuracion_Roles.md    # Configuración inicial
    ├── T024_Vistas_Gestion.md         # Interfaces web
    └── T034_Documentacion_API.md      # Documentación API
```

## 🎯 Casos de Uso Implementados

### **CU1: Iniciar Sesión (Web/Móvil)**
**Ubicación:** `CU1_Autenticacion/`  
**Estado:** ✅ Completado  
**Descripción:** Sistema completo de autenticación con validaciones, bloqueo por intentos fallidos y auditoría básica.

### **CU2: Cerrar Sesión (Web/Móvil)**
**Ubicación:** `CU2_Logout_Sesion/`  
**Estado:** ✅ Completado  
**Descripción:** Gestión avanzada de sesiones con logout seguro, invalidación de sesiones y bitácora extendida.

### **CU3: Gestionar Socios (Alta, Edición, Inhabilitar/Reactivar)**
**Ubicación:** `CU3_Gestion_Socios/`  
**Estado:** ✅ Completado  
**Descripción:** CRUD completo de socios con validaciones robustas, búsquedas avanzadas y reportes.

### **CU4: Gestionar Parcelas por Socio**
**Ubicación:** `CU4_Gestion_Parcelas/`  
**Estado:** ✅ Completado  
**Descripción:** Gestión completa de parcelas con validaciones de superficie, coordenadas y documentación técnica.

### **CU5: Consultar Socios y Parcelas con Filtros (Web/Móvil)**
**Ubicación:** `CU5_Consultas_Filtros/`  
**Estado:** ✅ Completado  
**Descripción:** Sistema avanzado de consultas con filtros múltiples, vistas móviles y reportes básicos.

### **CU6: Gestionar Roles y Permisos**
**Ubicación:** `CU6_Roles_Permisos/`  
**Estado:** ✅ Completado  
**Descripción:** Sistema completo de roles y permisos con configuración inicial y documentación API.

## 📊 Métricas del Sistema

- **✅ 6 Casos de Uso** completamente implementados
- **✅ 113 Tests** automatizados pasando
- **✅ 50+ Endpoints** API funcionales
- **✅ 15+ Modelos** de datos validados
- **✅ Documentación completa** por CU y tarea

## 🚀 Inicio Rápido

Para comenzar a explorar la documentación:

1. **Visión General:** `IMPLEMENTATION_SUMMARY.md`
2. **API Completa:** `API_Documentation.md`
3. **Por CU específico:** Navegar a la carpeta correspondiente

## 📞 Contacto y Soporte

- **API Base:** `http://localhost:8000/api/`
- **Admin Panel:** `http://localhost:8000/admin/`
- **Tests:** `python manage.py test`
- **Documentación:** `docs/` directory

---

**📅 Última actualización:** Septiembre 2025  
**🎯 Estado del proyecto:** Completado al 100%</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\README.md