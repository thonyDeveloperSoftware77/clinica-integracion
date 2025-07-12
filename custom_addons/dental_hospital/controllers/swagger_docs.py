from odoo import http
from odoo.http import request
import os
import json


class SwaggerDocsController(http.Controller):
    """
    Controlador para servir la documentación Swagger/OpenAPI
    """

    @http.route('/api/v1/docs', type='http', auth='none', methods=['GET'], csrf=False)
    def swagger_ui(self, **kwargs):
        """
        Servir la interfaz de Swagger UI para la documentación de la API
        """
        swagger_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dental Hospital API - Documentación</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
        .swagger-ui .topbar {
            background-color: #2c3e50;
        }
        .swagger-ui .topbar .download-url-wrapper {
            display: none;
        }
        .swagger-ui .info {
            margin: 50px 0;
        }
        .swagger-ui .info .title {
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/v1/openapi.yaml',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null,
                tryItOutEnabled: true,
                supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                docExpansion: 'list',
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                showExtensions: true,
                showCommonExtensions: true
            });
        };
    </script>
</body>
</html>
        """
        
        return request.make_response(
            swagger_html,
            headers=[('Content-Type', 'text/html; charset=utf-8')]
        )

    @http.route('/api/v1/openapi.yaml', type='http', auth='none', methods=['GET'], csrf=False)
    def openapi_spec(self, **kwargs):
        """
        Servir el archivo de especificación OpenAPI en formato YAML
        """
        try:
            # Buscar el archivo swagger en el directorio docs
            module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(module_path)))
            swagger_file = os.path.join(project_root, 'docs', 'api-swagger.yaml')
            
            if os.path.exists(swagger_file):
                with open(swagger_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/x-yaml; charset=utf-8'),
                        ('Access-Control-Allow-Origin', '*'),
                        ('Access-Control-Allow-Methods', 'GET'),
                        ('Access-Control-Allow-Headers', 'Content-Type')
                    ]
                )
            else:
                # Fallback con especificación básica
                basic_spec = {
                    "openapi": "3.0.3",
                    "info": {
                        "title": "Dental Hospital API",
                        "version": "1.0.0",
                        "description": "API REST para gestión de clínica dental"
                    },
                    "paths": {
                        "/api/v1/info": {
                            "get": {
                                "summary": "Información de la API",
                                "responses": {
                                    "200": {
                                        "description": "Información obtenida exitosamente"
                                    }
                                }
                            }
                        }
                    }
                }
                
                import yaml
                content = yaml.dump(basic_spec, default_flow_style=False, allow_unicode=True)
                
                return request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/x-yaml; charset=utf-8'),
                        ('Access-Control-Allow-Origin', '*')
                    ]
                )
                
        except Exception as e:
            error_response = f"""
openapi: 3.0.3
info:
  title: Dental Hospital API
  version: 1.0.0
  description: Error loading API specification - {str(e)}
paths:
  /api/v1/info:
    get:
      summary: API Info
      responses:
        '200':
          description: Success
"""
            return request.make_response(
                error_response,
                headers=[('Content-Type', 'application/x-yaml; charset=utf-8')]
            )

    @http.route('/api/v1/openapi.json', type='http', auth='none', methods=['GET'], csrf=False)
    def openapi_json(self, **kwargs):
        """
        Servir el archivo de especificación OpenAPI en formato JSON
        """
        try:
            # Ejemplo básico en JSON
            spec = {
                "openapi": "3.0.3",
                "info": {
                    "title": "Dental Hospital API",
                    "version": "1.0.0",
                    "description": "API REST para gestión de clínica dental",
                    "contact": {
                        "name": "Soporte Técnico",
                        "email": "support@dentalhospital.com"
                    }
                },
                "servers": [
                    {
                        "url": "/",
                        "description": "Servidor actual"
                    }
                ],
                "paths": {
                    "/api/v1/info": {
                        "get": {
                            "tags": ["System"],
                            "summary": "Información de la API",
                            "description": "Obtiene información general sobre la API",
                            "responses": {
                                "200": {
                                    "description": "Información obtenida exitosamente",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object",
                                                "properties": {
                                                    "success": {"type": "boolean"},
                                                    "data": {"type": "object"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "/api/v1/incidents": {
                        "get": {
                            "tags": ["Incidents"],
                            "summary": "Listar reportes de incidentes",
                            "security": [{"odooAuth": []}],
                            "parameters": [
                                {
                                    "name": "limit",
                                    "in": "query",
                                    "schema": {"type": "integer", "default": 10}
                                },
                                {
                                    "name": "offset",
                                    "in": "query",
                                    "schema": {"type": "integer", "default": 0}
                                }
                            ],
                            "responses": {
                                "200": {
                                    "description": "Lista de incidentes obtenida exitosamente"
                                }
                            }
                        },
                        "post": {
                            "tags": ["Incidents"],
                            "summary": "Crear nuevo reporte de incidente",
                            "security": [{"odooAuth": []}],
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "required": ["title", "description", "incident_type", "urgency"],
                                            "properties": {
                                                "title": {"type": "string"},
                                                "description": {"type": "string"},
                                                "incident_type": {"type": "string"},
                                                "urgency": {
                                                    "type": "string",
                                                    "enum": ["low", "medium", "high", "urgent"]
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "responses": {
                                "200": {
                                    "description": "Incidente creado exitosamente"
                                }
                            }
                        }
                    }
                },
                "components": {
                    "securitySchemes": {
                        "odooAuth": {
                            "type": "http",
                            "scheme": "basic",
                            "description": "Autenticación básica de Odoo"
                        }
                    }
                },
                "tags": [
                    {"name": "System", "description": "Información del sistema"},
                    {"name": "Incidents", "description": "Gestión de reportes de incidentes"},
                    {"name": "Patients", "description": "Administración de pacientes"},
                    {"name": "Appointments", "description": "Programación de citas"},
                    {"name": "Prescriptions", "description": "Manejo de prescripciones"}
                ]
            }
            
            return request.make_response(
                json.dumps(spec, indent=2, ensure_ascii=False),
                headers=[
                    ('Content-Type', 'application/json; charset=utf-8'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET'),
                    ('Access-Control-Allow-Headers', 'Content-Type')
                ]
            )
            
        except Exception as e:
            error_spec = {
                "openapi": "3.0.3",
                "info": {
                    "title": "Dental Hospital API",
                    "version": "1.0.0",
                    "description": f"Error loading API specification: {str(e)}"
                },
                "paths": {}
            }
            
            return request.make_response(
                json.dumps(error_spec, indent=2),
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )
