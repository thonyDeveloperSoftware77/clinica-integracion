# Dental Hospital API - Documentación

## Introducción

La **Dental Hospital API** es una API REST que proporciona endpoints para la gestión integral de una clínica dental. Esta API está construida sobre Odoo y permite la administración de:

- 📋 **Reportes de Incidentes** - Gestión de incidencias y tickets de soporte
- 👥 **Pacientes** - Administración de información de pacientes
- 📅 **Citas** - Programación y gestión de citas médicas
- 💊 **Prescripciones** - Manejo de prescripciones médicas

## Base URL

```
http://localhost:8069  # Desarrollo
https://clinic.example.com  # Producción
```

## Autenticación

La API utiliza autenticación básica HTTP con las credenciales de usuario de Odoo:

```bash
# Autenticación básica
curl -u "username:password" http://localhost:8069/api/v1/info
```

## Endpoints Principales

### 📊 Información del Sistema

#### GET /api/v1/info
Obtiene información general de la API.

**Ejemplo de uso:**
```bash
curl -X GET "http://localhost:8069/api/v1/info" \
  -H "Content-Type: application/json"
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "name": "Dental Hospital API",
    "version": "1.0.0",
    "description": "API REST para gestión de clínica dental",
    "documentation": "/api/v1/docs",
    "endpoints": {
      "incidents": {...},
      "patients": {...}
    }
  }
}
```

### 📋 Gestión de Incidentes

#### GET /api/v1/incidents
Lista todos los reportes de incidentes.

**Parámetros de consulta:**
- `limit` (int): Número máximo de resultados (default: 10)
- `offset` (int): Número de resultados a omitir (default: 0)
- `patient_id` (int): Filtrar por ID de paciente
- `state` (string): Filtrar por estado (draft, submitted, in_progress, resolved, closed)

**Ejemplo de uso:**
```bash
curl -u "admin:admin" \
  "http://localhost:8069/api/v1/incidents?limit=5&state=draft" \
  -H "Content-Type: application/json"
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Problema con cita médica",
      "description": "No pude asistir a mi cita programada",
      "incident_type": "scheduling",
      "urgency": "medium",
      "state": "draft",
      "patient_id": 123,
      "patient_name": "Juan Pérez",
      "user_email": "juan@example.com",
      "user_name": "Juan Pérez",
      "create_date": "2025-01-11T10:30:00Z",
      "write_date": "2025-01-11T11:45:00Z",
      "zammad_ticket_id": null
    }
  ],
  "total": 1,
  "count": 1
}
```

#### POST /api/v1/incidents
Crea un nuevo reporte de incidente.

**Cuerpo de la solicitud:**
```json
{
  "title": "Problema con cita médica",
  "description": "No pude asistir a mi cita programada debido a una emergencia",
  "incident_type": "scheduling",
  "urgency": "medium",
  "patient_id": 123
}
```

**Ejemplo de uso:**
```bash
curl -u "admin:admin" \
  -X POST "http://localhost:8069/api/v1/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Problema con cita médica",
    "description": "No pude asistir a mi cita programada",
    "incident_type": "scheduling",
    "urgency": "medium"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "title": "Problema con cita médica",
    "description": "No pude asistir a mi cita programada",
    "incident_type": "scheduling",
    "urgency": "medium",
    "state": "draft",
    "create_date": "2025-01-11T12:00:00Z"
  },
  "message": "Incidente creado exitosamente"
}
```

#### GET /api/v1/incidents/{incident_id}
Obtiene los detalles de un incidente específico.

**Ejemplo de uso:**
```bash
curl -u "admin:admin" \
  "http://localhost:8069/api/v1/incidents/1" \
  -H "Content-Type: application/json"
```

#### PUT /api/v1/incidents/{incident_id}
Actualiza un incidente existente.

**Cuerpo de la solicitud:**
```json
{
  "state": "in_progress",
  "urgency": "high"
}
```

**Ejemplo de uso:**
```bash
curl -u "admin:admin" \
  -X PUT "http://localhost:8069/api/v1/incidents/1" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "in_progress",
    "urgency": "high"
  }'
```

### 👥 Gestión de Pacientes

#### GET /api/v1/patients
Lista todos los pacientes.

**Parámetros de consulta:**
- `limit` (int): Número máximo de resultados
- `offset` (int): Número de resultados a omitir
- `search` (string): Buscar por nombre

**Ejemplo de uso:**
```bash
curl -u "admin:admin" \
  "http://localhost:8069/api/v1/patients?search=Juan&limit=10" \
  -H "Content-Type: application/json"
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "name": "Juan Pérez",
      "email": "juan@example.com",
      "phone": "+1234567890",
      "mobile": "+0987654321",
      "street": "Calle Principal 123",
      "city": "Ciudad",
      "country_id": 1,
      "country_name": "Colombia",
      "is_patient": true,
      "create_date": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "count": 1
}
```

#### GET /api/v1/patients/{patient_id}
Obtiene los detalles completos de un paciente específico.

**Ejemplo de uso:**
```bash
curl -u "admin:admin" \
  "http://localhost:8069/api/v1/patients/123" \
  -H "Content-Type: application/json"
```

### 📅 Gestión de Citas

#### GET /api/v1/appointments
Lista todas las citas médicas.

**Parámetros de consulta:**
- `limit` (int): Número máximo de resultados
- `offset` (int): Número de resultados a omitir
- `patient_id` (int): Filtrar por ID de paciente
- `doctor_id` (int): Filtrar por ID de doctor
- `date_from` (string): Fecha desde (YYYY-MM-DD)
- `date_to` (string): Fecha hasta (YYYY-MM-DD)
- `state` (string): Filtrar por estado

**Ejemplo de uso:**
```bash
curl -u "admin:admin" \
  "http://localhost:8069/api/v1/appointments?patient_id=123&date_from=2025-01-15" \
  -H "Content-Type: application/json"
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 456,
      "patient_id": 123,
      "patient_name": "Juan Pérez",
      "doctor_id": 789,
      "doctor_name": "Dr. Ana García",
      "appointment_date": "2025-01-15T14:30:00Z",
      "appointment_time": "14:30",
      "state": "scheduled",
      "notes": "Revisión general",
      "create_date": "2025-01-11T10:00:00Z"
    }
  ],
  "total": 1,
  "count": 1
}
```

### 💊 Gestión de Prescripciones

#### GET /api/v1/prescriptions
Lista todas las prescripciones médicas.

**Parámetros de consulta:**
- `limit` (int): Número máximo de resultados
- `offset` (int): Número de resultados a omitir
- `patient_id` (int): Filtrar por ID de paciente
- `doctor_id` (int): Filtrar por ID de doctor

**Ejemplo de uso:**
```bash
curl -u "admin:admin" \
  "http://localhost:8069/api/v1/prescriptions?patient_id=123" \
  -H "Content-Type: application/json"
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 789,
      "sequence_no": "PRESC/2025/001",
      "patient_id": 123,
      "patient_name": "Juan Pérez",
      "doctor_id": 456,
      "doctor_name": "Dr. Ana García",
      "prescription_date": "2025-01-11T15:00:00Z",
      "state": "active",
      "notes": "Tomar con las comidas",
      "create_date": "2025-01-11T15:00:00Z"
    }
  ],
  "total": 1,
  "count": 1
}
```

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Éxito |
| 400 | Solicitud incorrecta |
| 401 | No autorizado |
| 403 | Acceso denegado |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

## Formato de Respuestas

Todas las respuestas de la API siguen el siguiente formato estándar:

### Respuesta exitosa:
```json
{
  "success": true,
  "data": {...},
  "total": 100,     // Solo en listas
  "count": 10       // Solo en listas
}
```

### Respuesta de error:
```json
{
  "success": false,
  "error": "Descripción técnica del error",
  "message": "Mensaje amigable para el usuario"
}
```

## Paginación

Los endpoints que devuelven listas soportan paginación mediante los parámetros:

- `limit`: Número máximo de elementos a devolver (máximo: 100, default: 10)
- `offset`: Número de elementos a omitir desde el inicio

**Ejemplo:**
```bash
# Obtener elementos 21-30 (página 3 con 10 elementos por página)
curl -u "admin:admin" \
  "http://localhost:8069/api/v1/incidents?limit=10&offset=20"
```

## Filtros

### Filtros por fecha
Para endpoints que soportan filtros por fecha, usa el formato ISO 8601:

```bash
# Filtrar citas para una fecha específica
curl -u "admin:admin" \
  "http://localhost:8069/api/v1/appointments?date_from=2025-01-15&date_to=2025-01-15"
```

### Filtros por estado
Los estados disponibles varían según el endpoint:

**Incidentes:**
- `draft` - Borrador
- `submitted` - Enviado
- `in_progress` - En progreso
- `resolved` - Resuelto
- `closed` - Cerrado

## Manejo de Errores

### Error de autenticación (401):
```json
{
  "success": false,
  "error": "No autorizado",
  "message": "Credenciales inválidas"
}
```

### Error de permisos (403):
```json
{
  "success": false,
  "error": "Acceso denegado",
  "message": "No tiene permisos para realizar esta acción"
}
```

### Error de validación (400):
```json
{
  "success": false,
  "error": "Campo requerido: title",
  "message": "Datos incompletos"
}
```

## Documentación Interactiva

Visita `/api/v1/docs` en tu navegador para acceder a la documentación interactiva de Swagger UI, donde puedes:

- Explorar todos los endpoints
- Probar las llamadas a la API directamente
- Ver ejemplos de respuestas
- Descargar la especificación OpenAPI

```
http://localhost:8069/api/v1/docs
```

## Especificación OpenAPI

La especificación completa de la API está disponible en:

- **YAML:** `/api/v1/openapi.yaml`
- **JSON:** `/api/v1/openapi.json`

## Ejemplos de Integración

### JavaScript (Fetch API)
```javascript
// Obtener lista de incidentes
async function getIncidents() {
  const response = await fetch('/api/v1/incidents', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ' + btoa('username:password')
    }
  });
  
  const data = await response.json();
  return data;
}

// Crear nuevo incidente
async function createIncident(incidentData) {
  const response = await fetch('/api/v1/incidents', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ' + btoa('username:password')
    },
    body: JSON.stringify(incidentData)
  });
  
  const data = await response.json();
  return data;
}
```

### Python (requests)
```python
import requests
from requests.auth import HTTPBasicAuth

# Configuración
base_url = "http://localhost:8069"
auth = HTTPBasicAuth('username', 'password')

# Obtener lista de incidentes
def get_incidents(limit=10, offset=0):
    url = f"{base_url}/api/v1/incidents"
    params = {'limit': limit, 'offset': offset}
    
    response = requests.get(url, params=params, auth=auth)
    return response.json()

# Crear nuevo incidente
def create_incident(title, description, incident_type, urgency):
    url = f"{base_url}/api/v1/incidents"
    data = {
        'title': title,
        'description': description,
        'incident_type': incident_type,
        'urgency': urgency
    }
    
    response = requests.post(url, json=data, auth=auth)
    return response.json()
```

### PHP (cURL)
```php
<?php
// Configuración
$base_url = "http://localhost:8069";
$username = "username";
$password = "password";

// Función para hacer llamadas a la API
function callAPI($method, $url, $data = null) {
    global $username, $password;
    
    $curl = curl_init();
    
    curl_setopt_array($curl, array(
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CUSTOMREQUEST => $method,
        CURLOPT_HTTPHEADER => array(
            "Content-Type: application/json"
        ),
        CURLOPT_USERPWD => "$username:$password"
    ));
    
    if ($data) {
        curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
    }
    
    $response = curl_exec($curl);
    curl_close($curl);
    
    return json_decode($response, true);
}

// Obtener lista de incidentes
function getIncidents($limit = 10, $offset = 0) {
    global $base_url;
    $url = "$base_url/api/v1/incidents?limit=$limit&offset=$offset";
    return callAPI('GET', $url);
}

// Crear nuevo incidente
function createIncident($title, $description, $incident_type, $urgency) {
    global $base_url;
    $url = "$base_url/api/v1/incidents";
    $data = array(
        'title' => $title,
        'description' => $description,
        'incident_type' => $incident_type,
        'urgency' => $urgency
    );
    return callAPI('POST', $url, $data);
}
?>
```

## Soporte

Para soporte técnico o preguntas sobre la API, contacta:

- **Email:** support@dentalhospital.com
- **Documentación:** http://localhost:8069/api/v1/docs
- **Repositorio:** [GitHub Repository]

## Licencia

Esta API está licenciada bajo la licencia MIT.
