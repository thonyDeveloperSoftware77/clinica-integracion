from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, MissingError, ValidationError
import json
import datetime
from werkzeug.exceptions import BadRequest


class DentalHospitalAPI(http.Controller):
    """
    API REST para Clínica Dental
    Proporciona endpoints para la gestión de pacientes, citas, reportes de incidentes y prescripciones
    """

    # ======================== INCIDENT REPORTS API ========================
    
    @http.route('/api/v1/incidents', type='json', auth='user', methods=['GET'], csrf=False)
    def get_incidents(self, **kwargs):
        """
        Obtener lista de reportes de incidentes
        
        Query Parameters:
        - limit: int (default 10)
        - offset: int (default 0)
        - patient_id: int (opcional)
        - state: str (opcional: draft, submitted, in_progress, resolved, closed)
        
        Returns:
        {
            "success": true,
            "data": [...],
            "total": int,
            "count": int
        }
        """
        try:
            limit = kwargs.get('limit', 10)
            offset = kwargs.get('offset', 0)
            patient_id = kwargs.get('patient_id')
            state = kwargs.get('state')
            
            domain = []
            
            # Filtro por paciente
            if patient_id:
                domain.append(('patient_id', '=', patient_id))
            
            # Filtro por estado
            if state:
                domain.append(('state', '=', state))
            
            # Solo incidentes del usuario actual si no es admin
            if not request.env.user.has_group('dental_hospital.group_dental_manager'):
                domain.append(('patient_id.user_ids', 'in', [request.env.user.id]))
            
            incidents = request.env['incident.report'].search(domain, limit=limit, offset=offset)
            total = request.env['incident.report'].search_count(domain)
            
            data = []
            for incident in incidents:
                data.append({
                    'id': incident.id,
                    'title': incident.title,
                    'description': incident.description,
                    'incident_type': incident.incident_type,
                    'urgency': incident.urgency,
                    'state': incident.state,
                    'patient_id': incident.patient_id.id if incident.patient_id else None,
                    'patient_name': incident.patient_id.name if incident.patient_id else None,
                    'user_email': incident.user_email,
                    'user_name': incident.user_name,
                    'create_date': incident.create_date.isoformat() if incident.create_date else None,
                    'write_date': incident.write_date.isoformat() if incident.write_date else None,
                    'zammad_ticket_id': incident.zammad_ticket_id,
                })
            
            return {
                'success': True,
                'data': data,
                'total': total,
                'count': len(data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al obtener reportes de incidentes'
            }

    @http.route('/api/v1/incidents', type='json', auth='user', methods=['POST'], csrf=False)
    def create_incident(self, **kwargs):
        """
        Crear nuevo reporte de incidente
        
        Body Parameters:
        {
            "title": "string (required)",
            "description": "string (required)",
            "incident_type": "string (required)",
            "urgency": "string (required: low, medium, high, urgent)",
            "patient_id": int (optional)
        }
        
        Returns:
        {
            "success": true,
            "data": {...},
            "message": "Incidente creado exitosamente"
        }
        """
        try:
            data = kwargs
            
            # Validaciones
            required_fields = ['title', 'description', 'incident_type', 'urgency']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'success': False,
                        'error': f'Campo requerido: {field}',
                        'message': 'Datos incompletos'
                    }
            
            # Crear el incidente
            incident_data = {
                'title': data['title'],
                'description': data['description'],
                'incident_type': data['incident_type'],
                'urgency': data['urgency'],
                'user_email': request.env.user.email,
                'user_name': request.env.user.name,
                'state': 'draft'
            }
            
            if data.get('patient_id'):
                incident_data['patient_id'] = data['patient_id']
            
            incident = request.env['incident.report'].create(incident_data)
            
            return {
                'success': True,
                'data': {
                    'id': incident.id,
                    'title': incident.title,
                    'description': incident.description,
                    'incident_type': incident.incident_type,
                    'urgency': incident.urgency,
                    'state': incident.state,
                    'create_date': incident.create_date.isoformat()
                },
                'message': 'Incidente creado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al crear el incidente'
            }

    @http.route('/api/v1/incidents/<int:incident_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_incident(self, incident_id, **kwargs):
        """
        Obtener detalles de un incidente específico
        
        Path Parameters:
        - incident_id: int (required)
        
        Returns:
        {
            "success": true,
            "data": {...}
        }
        """
        try:
            incident = request.env['incident.report'].browse(incident_id)
            
            if not incident.exists():
                return {
                    'success': False,
                    'error': 'Incidente no encontrado',
                    'message': 'El incidente especificado no existe'
                }
            
            # Verificar permisos
            if not request.env.user.has_group('dental_hospital.group_dental_manager'):
                if not incident.patient_id or request.env.user.id not in incident.patient_id.user_ids.ids:
                    return {
                        'success': False,
                        'error': 'Acceso denegado',
                        'message': 'No tiene permisos para ver este incidente'
                    }
            
            return {
                'success': True,
                'data': {
                    'id': incident.id,
                    'title': incident.title,
                    'description': incident.description,
                    'incident_type': incident.incident_type,
                    'urgency': incident.urgency,
                    'state': incident.state,
                    'patient_id': incident.patient_id.id if incident.patient_id else None,
                    'patient_name': incident.patient_id.name if incident.patient_id else None,
                    'user_email': incident.user_email,
                    'user_name': incident.user_name,
                    'create_date': incident.create_date.isoformat() if incident.create_date else None,
                    'write_date': incident.write_date.isoformat() if incident.write_date else None,
                    'zammad_ticket_id': incident.zammad_ticket_id,
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al obtener el incidente'
            }

    @http.route('/api/v1/incidents/<int:incident_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_incident(self, incident_id, **kwargs):
        """
        Actualizar un incidente existente
        
        Path Parameters:
        - incident_id: int (required)
        
        Body Parameters:
        {
            "title": "string (optional)",
            "description": "string (optional)",
            "urgency": "string (optional)",
            "state": "string (optional)"
        }
        
        Returns:
        {
            "success": true,
            "data": {...},
            "message": "Incidente actualizado exitosamente"
        }
        """
        try:
            incident = request.env['incident.report'].browse(incident_id)
            
            if not incident.exists():
                return {
                    'success': False,
                    'error': 'Incidente no encontrado',
                    'message': 'El incidente especificado no existe'
                }
            
            # Verificar permisos
            if not request.env.user.has_group('dental_hospital.group_dental_manager'):
                if not incident.patient_id or request.env.user.id not in incident.patient_id.user_ids.ids:
                    return {
                        'success': False,
                        'error': 'Acceso denegado',
                        'message': 'No tiene permisos para editar este incidente'
                    }
            
            # Actualizar campos permitidos
            update_data = {}
            allowed_fields = ['title', 'description', 'urgency', 'state']
            
            for field in allowed_fields:
                if field in kwargs:
                    update_data[field] = kwargs[field]
            
            if update_data:
                incident.write(update_data)
            
            return {
                'success': True,
                'data': {
                    'id': incident.id,
                    'title': incident.title,
                    'description': incident.description,
                    'urgency': incident.urgency,
                    'state': incident.state,
                    'write_date': incident.write_date.isoformat()
                },
                'message': 'Incidente actualizado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al actualizar el incidente'
            }

    # ======================== PATIENTS API ========================
    
    @http.route('/api/v1/patients', type='json', auth='user', methods=['GET'], csrf=False)
    def get_patients(self, **kwargs):
        """
        Obtener lista de pacientes
        
        Query Parameters:
        - limit: int (default 10)
        - offset: int (default 0)
        - search: str (opcional - buscar por nombre)
        
        Returns:
        {
            "success": true,
            "data": [...],
            "total": int,
            "count": int
        }
        """
        try:
            limit = kwargs.get('limit', 10)
            offset = kwargs.get('offset', 0)
            search = kwargs.get('search', '')
            
            domain = []
            
            # Búsqueda por nombre
            if search:
                domain.append(('name', 'ilike', search))
            
            # Solo pacientes del usuario actual si no es admin/manager
            if not request.env.user.has_group('dental_hospital.group_dental_manager'):
                domain.append(('user_ids', 'in', [request.env.user.id]))
            
            patients = request.env['res.partner'].search(domain, limit=limit, offset=offset)
            total = request.env['res.partner'].search_count(domain)
            
            data = []
            for patient in patients:
                data.append({
                    'id': patient.id,
                    'name': patient.name,
                    'email': patient.email,
                    'phone': patient.phone,
                    'mobile': patient.mobile,
                    'street': patient.street,
                    'city': patient.city,
                    'country_id': patient.country_id.id if patient.country_id else None,
                    'country_name': patient.country_id.name if patient.country_id else None,
                    'is_patient': getattr(patient, 'is_patient', False),
                    'create_date': patient.create_date.isoformat() if patient.create_date else None,
                })
            
            return {
                'success': True,
                'data': data,
                'total': total,
                'count': len(data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al obtener pacientes'
            }

    @http.route('/api/v1/patients/<int:patient_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_patient(self, patient_id, **kwargs):
        """
        Obtener detalles de un paciente específico
        
        Path Parameters:
        - patient_id: int (required)
        
        Returns:
        {
            "success": true,
            "data": {...}
        }
        """
        try:
            patient = request.env['res.partner'].browse(patient_id)
            
            if not patient.exists():
                return {
                    'success': False,
                    'error': 'Paciente no encontrado',
                    'message': 'El paciente especificado no existe'
                }
            
            # Verificar permisos
            if not request.env.user.has_group('dental_hospital.group_dental_manager'):
                if request.env.user.id not in patient.user_ids.ids:
                    return {
                        'success': False,
                        'error': 'Acceso denegado',
                        'message': 'No tiene permisos para ver este paciente'
                    }
            
            return {
                'success': True,
                'data': {
                    'id': patient.id,
                    'name': patient.name,
                    'email': patient.email,
                    'phone': patient.phone,
                    'mobile': patient.mobile,
                    'street': patient.street,
                    'city': patient.city,
                    'state_id': patient.state_id.id if patient.state_id else None,
                    'state_name': patient.state_id.name if patient.state_id else None,
                    'country_id': patient.country_id.id if patient.country_id else None,
                    'country_name': patient.country_id.name if patient.country_id else None,
                    'zip': patient.zip,
                    'is_patient': getattr(patient, 'is_patient', False),
                    'create_date': patient.create_date.isoformat() if patient.create_date else None,
                    'write_date': patient.write_date.isoformat() if patient.write_date else None,
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al obtener el paciente'
            }

    # ======================== APPOINTMENTS API ========================
    
    @http.route('/api/v1/appointments', type='json', auth='user', methods=['GET'], csrf=False)
    def get_appointments(self, **kwargs):
        """
        Obtener lista de citas
        
        Query Parameters:
        - limit: int (default 10)
        - offset: int (default 0)
        - patient_id: int (opcional)
        - doctor_id: int (opcional)
        - date_from: str (opcional, formato: YYYY-MM-DD)
        - date_to: str (opcional, formato: YYYY-MM-DD)
        - state: str (opcional)
        
        Returns:
        {
            "success": true,
            "data": [...],
            "total": int,
            "count": int
        }
        """
        try:
            limit = kwargs.get('limit', 10)
            offset = kwargs.get('offset', 0)
            patient_id = kwargs.get('patient_id')
            doctor_id = kwargs.get('doctor_id')
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            state = kwargs.get('state')
            
            domain = []
            
            # Filtros
            if patient_id:
                domain.append(('patient_id', '=', patient_id))
            
            if doctor_id:
                domain.append(('doctor_id', '=', doctor_id))
            
            if date_from:
                domain.append(('appointment_date', '>=', date_from))
            
            if date_to:
                domain.append(('appointment_date', '<=', date_to))
            
            if state:
                domain.append(('state', '=', state))
            
            # Solo citas del usuario actual si no es admin/manager
            if not request.env.user.has_group('dental_hospital.group_dental_manager'):
                domain.append(('patient_id.user_ids', 'in', [request.env.user.id]))
            
            appointments = request.env['dental.appointment'].search(domain, limit=limit, offset=offset)
            total = request.env['dental.appointment'].search_count(domain)
            
            data = []
            for appointment in appointments:
                data.append({
                    'id': appointment.id,
                    'patient_id': appointment.patient_id.id if appointment.patient_id else None,
                    'patient_name': appointment.patient_id.name if appointment.patient_id else None,
                    'doctor_id': appointment.doctor_id.id if appointment.doctor_id else None,
                    'doctor_name': appointment.doctor_id.name if appointment.doctor_id else None,
                    'appointment_date': appointment.appointment_date.isoformat() if appointment.appointment_date else None,
                    'appointment_time': str(appointment.appointment_time) if hasattr(appointment, 'appointment_time') else None,
                    'state': getattr(appointment, 'state', None),
                    'notes': getattr(appointment, 'notes', None),
                    'create_date': appointment.create_date.isoformat() if appointment.create_date else None,
                })
            
            return {
                'success': True,
                'data': data,
                'total': total,
                'count': len(data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al obtener citas'
            }

    # ======================== PRESCRIPTIONS API ========================
    
    @http.route('/api/v1/prescriptions', type='json', auth='user', methods=['GET'], csrf=False)
    def get_prescriptions(self, **kwargs):
        """
        Obtener lista de prescripciones
        
        Query Parameters:
        - limit: int (default 10)
        - offset: int (default 0)
        - patient_id: int (opcional)
        - doctor_id: int (opcional)
        
        Returns:
        {
            "success": true,
            "data": [...],
            "total": int,
            "count": int
        }
        """
        try:
            limit = kwargs.get('limit', 10)
            offset = kwargs.get('offset', 0)
            patient_id = kwargs.get('patient_id')
            doctor_id = kwargs.get('doctor_id')
            
            domain = []
            
            # Filtros
            if patient_id:
                domain.append(('patient_id', '=', patient_id))
            
            if doctor_id:
                domain.append(('doctor_id', '=', doctor_id))
            
            # Solo prescripciones del usuario actual si no es admin/manager
            if not request.env.user.has_group('dental_hospital.group_dental_manager'):
                domain.append(('patient_id.user_ids', 'in', [request.env.user.id]))
            
            prescriptions = request.env['dental.prescription'].search(domain, limit=limit, offset=offset)
            total = request.env['dental.prescription'].search_count(domain)
            
            data = []
            for prescription in prescriptions:
                data.append({
                    'id': prescription.id,
                    'sequence_no': prescription.sequence_no,
                    'patient_id': prescription.patient_id.id if prescription.patient_id else None,
                    'patient_name': prescription.patient_id.name if prescription.patient_id else None,
                    'doctor_id': prescription.doctor_id.id if prescription.doctor_id else None,
                    'doctor_name': prescription.doctor_id.name if prescription.doctor_id else None,
                    'prescription_date': prescription.prescription_date.isoformat() if prescription.prescription_date else None,
                    'state': getattr(prescription, 'state', None),
                    'notes': getattr(prescription, 'notes', None),
                    'create_date': prescription.create_date.isoformat() if prescription.create_date else None,
                })
            
            return {
                'success': True,
                'data': data,
                'total': total,
                'count': len(data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al obtener prescripciones'
            }

    # ======================== SYSTEM INFO API ========================
    
    @http.route('/api/v1/info', type='json', auth='none', methods=['GET'], csrf=False)
    def get_api_info(self, **kwargs):
        """
        Obtener información de la API
        
        Returns:
        {
            "success": true,
            "data": {
                "name": "Dental Hospital API",
                "version": "1.0.0",
                "description": "API REST para gestión de clínica dental",
                "endpoints": [...]
            }
        }
        """
        return {
            'success': True,
            'data': {
                'name': 'Dental Hospital API',
                'version': '1.0.0',
                'description': 'API REST para gestión de clínica dental',
                'documentation': '/api/v1/docs',
                'endpoints': {
                    'incidents': {
                        'GET /api/v1/incidents': 'Listar reportes de incidentes',
                        'POST /api/v1/incidents': 'Crear nuevo reporte de incidente',
                        'GET /api/v1/incidents/{id}': 'Obtener detalles de incidente',
                        'PUT /api/v1/incidents/{id}': 'Actualizar incidente'
                    },
                    'patients': {
                        'GET /api/v1/patients': 'Listar pacientes',
                        'GET /api/v1/patients/{id}': 'Obtener detalles de paciente'
                    },
                    'appointments': {
                        'GET /api/v1/appointments': 'Listar citas'
                    },
                    'prescriptions': {
                        'GET /api/v1/prescriptions': 'Listar prescripciones'
                    },
                    'system': {
                        'GET /api/v1/info': 'Información de la API'
                    }
                }
            }
        }
