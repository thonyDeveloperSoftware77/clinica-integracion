# Instalación y Configuración del Módulo de Reportes de Incidentes

## Pasos de Instalación

### 1. Instalar Dependencias de Python
```bash
pip install requests
```

### 2. Actualizar el Módulo en Odoo
1. Ir a **Aplicaciones** en Odoo
2. Buscar "Dental Hospital Management"
3. Hacer clic en **Actualizar**

### 3. Configurar la Integración con Zammad

#### En Zammad:
1. Ir a **Admin Panel > Channels > API**
2. Habilitar "Token Access"
3. Crear un token de acceso para el usuario que manejará los tickets

#### En Odoo:
1. Ir a **Configuración > Configuración General**
2. Buscar la sección "Zammad Integration"
3. Configurar:
   - **Zammad URL**: URL de tu instancia de Zammad (ej: `http://localhost:8080`)
   - **Zammad API Token**: Token generado en Zammad
   - **Default Group ID**: ID del grupo por defecto para los tickets (normalmente `1`)

### 4. Configurar SSO con Clerk (OpenID Connect)

#### En Clerk:
1. Crear una aplicación OpenID Connect
2. Configurar las URLs de callback para Odoo y Zammad
3. Obtener los datos de configuración (Client ID, Client Secret, etc.)

#### En Odoo:
1. Instalar el módulo `auth_oauth`
2. Configurar el proveedor OAuth en **Configuración > Usuarios y Empresas > Proveedores OAuth**
3. Configurar los campos:
   - **Provider Name**: Clerk
   - **Client ID**: Client ID de Clerk
   - **Client Secret**: Client Secret de Clerk
   - **Authorization URL**: URL de autorización de Clerk
   - **Token URL**: URL de token de Clerk
   - **User Info URL**: URL de información del usuario de Clerk

#### En Zammad:
1. Ir a **Admin Panel > Security > Third-party Applications**
2. Configurar OpenID Connect con los datos de Clerk
3. Mapear los campos de usuario apropiados

### 5. Configurar Usuarios y Pacientes

#### Asociar Usuarios con Pacientes:
1. Ir a **Contactos** en Odoo
2. Para cada paciente, asegurar que:
   - El campo **Es un Paciente** esté marcado
   - El usuario esté asociado en el campo **Usuarios**
   - El email del usuario coincida con el email del paciente

### 6. Configurar Permisos

#### Grupos de Usuarios:
- **Usuarios del Portal**: Pueden crear y ver sus propios reportes de incidentes
- **Usuarios Internos**: Pueden ver y gestionar todos los reportes de incidentes

#### Permisos por Defecto:
- Los usuarios del portal solo pueden ver sus propios incidentes
- Los usuarios internos pueden ver todos los incidentes
- Los administradores pueden configurar la integración con Zammad

## Uso del Sistema

### Para Pacientes:
1. Iniciar sesión en el portal de pacientes
2. Ir a **Reportes de Incidentes**
3. Hacer clic en **Nuevo** para crear un reporte
4. Llenar el formulario con:
   - **Título**: Descripción breve del incidente
   - **Categoría**: Tipo de incidente
   - **Prioridad**: Nivel de urgencia
   - **Descripción**: Explicación detallada del problema
5. Hacer clic en **Enviar Reporte** para crear el ticket en Zammad

### Para Administradores:
1. Ir a **Reportes de Incidentes > Todos los Incidentes**
2. Ver el estado de todos los reportes
3. Seguir el progreso de los tickets en Zammad
4. Configurar la integración según sea necesario

## Solución de Problemas

### Errores Comunes:

#### "Error connecting to Zammad":
- Verificar que la URL de Zammad sea correcta
- Verificar que el token de API sea válido
- Verificar conectividad de red

#### "Patient not found":
- Asegurar que el usuario esté asociado con un registro de paciente
- Verificar que el campo **Es un Paciente** esté marcado
- Verificar que el email coincida

#### "Permission denied":
- Verificar que el usuario tenga los permisos correctos
- Verificar que el token de Zammad tenga permisos suficientes

### Logs y Debugging:
- Los logs se pueden encontrar en **Configuración > Técnico > Logging**
- Los errores de integración con Zammad se registran en el sistema de logs de Odoo

## Mantenimiento

### Actualización de Tokens:
- Los tokens de API de Zammad pueden necesitar renovación periódica
- Actualizar el token en **Configuración > Parámetros del Sistema**

### Monitoreo:
- Revisar regularmente los logs de errores
- Verificar que los tickets se estén creando correctamente en Zammad
- Monitorear el estado de los incidentes

### Backup:
- Incluir los reportes de incidentes en los backups regulares de Odoo
- Considerar backup de los datos de configuración de Zammad

## Soporte
Para problemas técnicos o preguntas sobre la configuración, contactar al equipo de desarrollo o crear un reporte de incidente a través del sistema.
