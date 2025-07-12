import json
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class RabbitMQService(models.AbstractModel):
    """Service for RabbitMQ integration"""
    _name = 'rabbitmq.service'
    _description = 'RabbitMQ Service'

    @api.model
    def send_to_queue(self, queue_name, message_data):
        """Send message to RabbitMQ queue"""
        try:
            # Try to import pika, if not available, use requests as fallback
            try:
                import pika
                return self._send_with_pika(queue_name, message_data)
            except ImportError:
                _logger.info('pika not available, using requests fallback')
                return self._send_with_requests(queue_name, message_data)
                
        except Exception as e:
            _logger.error(f'Failed to send message to RabbitMQ: {str(e)}')
            return False

    def _send_with_pika(self, queue_name, message_data):
        """Send message using pika library"""
        import pika
        
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq', port=5672)
        )
        channel = connection.channel()
        
        # Declare queue
        channel.queue_declare(queue=queue_name, durable=False)
        
        # Send message
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message_data)
        )
        
        connection.close()
        _logger.info(f'Message sent to {queue_name} via pika')
        return True

    def _send_with_requests(self, queue_name, message_data):
        """Send message using requests as fallback (via RabbitMQ Management API)"""
        import requests
        import base64
        
        try:
            # RabbitMQ Management API
            url = 'http://rabbitmq:15672/api/exchanges/%2F/amq.default/publish'
            
            # Basic auth for RabbitMQ
            auth = base64.b64encode(b'guest:guest').decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'properties': {},
                'routing_key': queue_name,
                'payload': json.dumps(message_data),
                'payload_encoding': 'string'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                _logger.info(f'Message sent to {queue_name} via Management API')
                return True
            else:
                _logger.error(f'Failed to send via Management API: {response.status_code}')
                return False
                
        except Exception as e:
            _logger.error(f'Failed to send via requests fallback: {str(e)}')
            return False
