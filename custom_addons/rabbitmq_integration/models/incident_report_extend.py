from odoo import api, models, _
import logging

_logger = logging.getLogger(__name__)


class IncidentReportExtend(models.Model):
    """Extend incident report model to add RabbitMQ integration"""
    _inherit = 'incident.report'

    @api.model
    def create(self, vals):
        """Override create to add RabbitMQ notification"""
        # Call original create method
        record = super(IncidentReportExtend, self).create(vals)
        
        # Send notification to RabbitMQ after successful creation
        try:
            self._send_rabbitmq_notification(record)
        except Exception as e:
            _logger.error(f'Failed to send RabbitMQ notification: {str(e)}')
            # Don't fail the creation if RabbitMQ fails
        
        return record
    
    def _send_rabbitmq_notification(self, record):
        """Send incident notification to RabbitMQ"""
        # Get RabbitMQ service
        rabbitmq_service = self.env['rabbitmq.service']
        
        # Prepare message data
        message_data = {
            'name': record.name,
            'description': record.description,
            'priority': record.priority,
            'user_name': record.user_name,
            'user_email': record.user_email,
            'state': record.state,
            'create_date': record.create_date.isoformat() if record.create_date else None,
        }
        
        # Send to zammad_alerts queue
        success = rabbitmq_service.send_to_queue('zammad_alerts', message_data)
        
        if success:
            _logger.info(f'Incident {record.name} notification sent to RabbitMQ')
        else:
            _logger.warning(f'Failed to send incident {record.name} to RabbitMQ')
