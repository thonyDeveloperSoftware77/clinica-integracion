#!/bin/bash

# =============================================================================
# DENTAL HOSPITAL API - EJEMPLOS DE PRUEBAS
# =============================================================================
# Este script contiene ejemplos de llamadas a la API para probar todos los endpoints
# 
# Uso:
#   1. Modifica las variables de configuración según tu entorno
#   2. Ejecuta: bash test_api_examples.sh
#   3. O ejecuta comandos individuales copiando y pegando
#
# Prerrequisitos:
#   - curl instalado
#   - jq instalado (opcional, para formatear JSON)
#   - Servidor Odoo ejecutándose
# =============================================================================

# Configuración
BASE_URL="http://localhost:8069"
USERNAME="admin"
PASSWORD="admin"
AUTH_HEADER="Authorization: Basic $(echo -n "$USERNAME:$PASSWORD" | base64)"

echo "🏥 DENTAL HOSPITAL API - EJEMPLOS DE PRUEBAS"
echo "============================================="
echo "Base URL: $BASE_URL"
echo "Usuario: $USERNAME"
echo ""

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

# Función para hacer llamadas GET
api_get() {
    local endpoint="$1"
    local params="$2"
    echo "📤 GET $endpoint"
    if [ -n "$params" ]; then
        endpoint="$endpoint?$params"
    fi
    curl -s -X GET "$BASE_URL$endpoint" \
        -H "Content-Type: application/json" \
        -H "$AUTH_HEADER" | jq '.' 2>/dev/null || cat
    echo ""
    echo "---"
}

# Función para hacer llamadas POST
api_post() {
    local endpoint="$1"
    local data="$2"
    echo "📤 POST $endpoint"
    echo "📋 Data: $data"
    curl -s -X POST "$BASE_URL$endpoint" \
        -H "Content-Type: application/json" \
        -H "$AUTH_HEADER" \
        -d "$data" | jq '.' 2>/dev/null || cat
    echo ""
    echo "---"
}

# Función para hacer llamadas PUT
api_put() {
    local endpoint="$1"
    local data="$2"
    echo "📤 PUT $endpoint"
    echo "📋 Data: $data"
    curl -s -X PUT "$BASE_URL$endpoint" \
        -H "Content-Type: application/json" \
        -H "$AUTH_HEADER" \
        -d "$data" | jq '.' 2>/dev/null || cat
    echo ""
    echo "---"
}

# =============================================================================
# 1. INFORMACIÓN DEL SISTEMA
# =============================================================================

echo "1️⃣  INFORMACIÓN DEL SISTEMA"
echo "============================"

# Obtener información de la API
api_get "/api/v1/info"

# =============================================================================
# 2. GESTIÓN DE INCIDENTES
# =============================================================================

echo "2️⃣  GESTIÓN DE INCIDENTES"
echo "========================="

# Listar todos los incidentes
api_get "/api/v1/incidents"

# Listar incidentes con límite
api_get "/api/v1/incidents" "limit=5&offset=0"

# Listar incidentes por estado
api_get "/api/v1/incidents" "state=draft"

# Crear nuevo incidente - Ejemplo 1: Problema de programación
api_post "/api/v1/incidents" '{
  "title": "No puedo agendar cita",
  "description": "El sistema no me permite seleccionar una fecha disponible para mi cita dental. Siempre aparece un mensaje de error cuando intento confirmar.",
  "incident_type": "scheduling",
  "urgency": "medium"
}'

# Crear nuevo incidente - Ejemplo 2: Problema médico
api_post "/api/v1/incidents" '{
  "title": "Dolor persistente después del tratamiento",
  "description": "Después del tratamiento de endodoncia realizado la semana pasada, sigo experimentando dolor intenso. El medicamento recetado no está funcionando.",
  "incident_type": "medical",
  "urgency": "high"
}'

# Crear nuevo incidente - Ejemplo 3: Problema técnico
api_post "/api/v1/incidents" '{
  "title": "Error en el portal de pacientes",
  "description": "No puedo acceder a mi historial médico desde el portal. La página se queda en blanco después de iniciar sesión.",
  "incident_type": "technical",
  "urgency": "low"
}'

# Crear nuevo incidente - Ejemplo 4: Problema de facturación
api_post "/api/v1/incidents" '{
  "title": "Cobro duplicado en mi cuenta",
  "description": "En mi estado de cuenta aparece un cobro duplicado por el mismo tratamiento. Necesito que verifiquen y corrijan este error.",
  "incident_type": "billing",
  "urgency": "medium"
}'

# Obtener detalles de un incidente específico (ID 1)
api_get "/api/v1/incidents/1"

# Actualizar un incidente
api_put "/api/v1/incidents/1" '{
  "state": "in_progress",
  "urgency": "high"
}'

# =============================================================================
# 3. GESTIÓN DE PACIENTES
# =============================================================================

echo "3️⃣  GESTIÓN DE PACIENTES"
echo "========================"

# Listar todos los pacientes
api_get "/api/v1/patients"

# Listar pacientes con límite y búsqueda
api_get "/api/v1/patients" "limit=10&search=Juan"

# Buscar pacientes por nombre parcial
api_get "/api/v1/patients" "search=Mar"

# Obtener detalles de un paciente específico (ID 1)
api_get "/api/v1/patients/1"

# =============================================================================
# 4. GESTIÓN DE CITAS
# =============================================================================

echo "4️⃣  GESTIÓN DE CITAS"
echo "==================="

# Listar todas las citas
api_get "/api/v1/appointments"

# Listar citas con filtros de fecha
api_get "/api/v1/appointments" "date_from=2025-01-15&date_to=2025-01-31"

# Listar citas de un paciente específico
api_get "/api/v1/appointments" "patient_id=1"

# Listar citas de un doctor específico
api_get "/api/v1/appointments" "doctor_id=1"

# Listar citas con múltiples filtros
api_get "/api/v1/appointments" "patient_id=1&date_from=2025-01-15&limit=5"

# =============================================================================
# 5. GESTIÓN DE PRESCRIPCIONES
# =============================================================================

echo "5️⃣  GESTIÓN DE PRESCRIPCIONES"
echo "============================="

# Listar todas las prescripciones
api_get "/api/v1/prescriptions"

# Listar prescripciones de un paciente específico
api_get "/api/v1/prescriptions" "patient_id=1"

# Listar prescripciones de un doctor específico
api_get "/api/v1/prescriptions" "doctor_id=1"

# Listar prescripciones con paginación
api_get "/api/v1/prescriptions" "limit=10&offset=0"

# =============================================================================
# 6. PRUEBAS DE ERRORES Y CASOS LÍMITE
# =============================================================================

echo "6️⃣  PRUEBAS DE ERRORES Y CASOS LÍMITE"
echo "====================================="

# Probar endpoint inexistente
echo "📤 GET /api/v1/nonexistent (Debe devolver 404)"
curl -s -X GET "$BASE_URL/api/v1/nonexistent" \
    -H "Content-Type: application/json" \
    -H "$AUTH_HEADER" | jq '.' 2>/dev/null || cat
echo ""
echo "---"

# Probar acceso sin autenticación
echo "📤 GET /api/v1/incidents (Sin autenticación - Debe devolver 401)"
curl -s -X GET "$BASE_URL/api/v1/incidents" \
    -H "Content-Type: application/json" | jq '.' 2>/dev/null || cat
echo ""
echo "---"

# Probar crear incidente con datos incompletos
echo "📤 POST /api/v1/incidents (Datos incompletos - Debe devolver 400)"
curl -s -X POST "$BASE_URL/api/v1/incidents" \
    -H "Content-Type: application/json" \
    -H "$AUTH_HEADER" \
    -d '{"title": "Solo título"}' | jq '.' 2>/dev/null || cat
echo ""
echo "---"

# Probar acceso a recurso inexistente
echo "📤 GET /api/v1/incidents/99999 (ID inexistente - Debe devolver 404)"
api_get "/api/v1/incidents/99999"

# Probar límites de paginación
echo "📤 GET /api/v1/incidents (Límite excesivo)"
api_get "/api/v1/incidents" "limit=1000"

# =============================================================================
# 7. PRUEBAS DE RENDIMIENTO BÁSICAS
# =============================================================================

echo "7️⃣  PRUEBAS DE RENDIMIENTO BÁSICAS"
echo "=================================="

# Medir tiempo de respuesta del endpoint de información
echo "⏱️  Midiendo tiempo de respuesta de /api/v1/info"
time curl -s -X GET "$BASE_URL/api/v1/info" \
    -H "Content-Type: application/json" > /dev/null
echo ""

# Prueba de carga ligera (10 llamadas concurrentes)
echo "🚀 Prueba de carga ligera (10 llamadas concurrentes)"
for i in {1..10}; do
    (curl -s -X GET "$BASE_URL/api/v1/info" \
        -H "Content-Type: application/json" > /dev/null) &
done
wait
echo "✅ Prueba completada"
echo ""

# =============================================================================
# 8. DOCUMENTACIÓN Y ESPECIFICACIONES
# =============================================================================

echo "8️⃣  DOCUMENTACIÓN Y ESPECIFICACIONES"
echo "===================================="

# Verificar acceso a documentación Swagger
echo "📖 Verificando documentación Swagger"
curl -s -I "$BASE_URL/api/v1/docs" | head -n 1
echo ""

# Verificar especificación OpenAPI YAML
echo "📄 Verificando especificación OpenAPI (YAML)"
curl -s -I "$BASE_URL/api/v1/openapi.yaml" | head -n 1
echo ""

# Verificar especificación OpenAPI JSON
echo "📄 Verificando especificación OpenAPI (JSON)"
curl -s -I "$BASE_URL/api/v1/openapi.json" | head -n 1
echo ""

# =============================================================================
# RESUMEN FINAL
# =============================================================================

echo "✅ PRUEBAS COMPLETADAS"
echo "======================"
echo ""
echo "📊 Resumen de endpoints probados:"
echo "  ✅ GET  /api/v1/info"
echo "  ✅ GET  /api/v1/incidents"
echo "  ✅ POST /api/v1/incidents"
echo "  ✅ GET  /api/v1/incidents/{id}"
echo "  ✅ PUT  /api/v1/incidents/{id}"
echo "  ✅ GET  /api/v1/patients"
echo "  ✅ GET  /api/v1/patients/{id}"
echo "  ✅ GET  /api/v1/appointments"
echo "  ✅ GET  /api/v1/prescriptions"
echo ""
echo "📖 Documentación disponible en:"
echo "  🌐 Swagger UI: $BASE_URL/api/v1/docs"
echo "  📄 OpenAPI YAML: $BASE_URL/api/v1/openapi.yaml"
echo "  📄 OpenAPI JSON: $BASE_URL/api/v1/openapi.json"
echo ""
echo "🎉 ¡Todas las pruebas han sido ejecutadas!"
