from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class ZammadConfig(models.Model):
    _name = 'zammad.config'
    _description = 'Zammad Configuration'
    _rec_name = 'name'

    name = fields.Char('Configuration Name', required=True, default='Zammad Server')
    url = fields.Char('Zammad URL', required=True, help='Base URL of Zammad instance (e.g., http://localhost:8080)')
    token = fields.Char('API Token', required=True, help='Zammad API Token')
    active = fields.Boolean('Active', default=True)
    
    @api.model
    def get_active_config(self):
        """Get the active Zammad configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise Exception("No active Zammad configuration found. Please configure Zammad settings.")
        return config
    
    def test_connection(self):
        """Test connection to Zammad API"""
        try:
            headers = {
                'Authorization': f'Token token={self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f'{self.url}/api/v1/users/me', headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Test',
                        'message': 'Successfully connected to Zammad!',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Test Failed',
                        'message': f'Failed to connect to Zammad: {response.status_code} - {response.text}',
                        'type': 'warning',
                        'sticky': True,
                    }
                }
        except Exception as e:
            _logger.error(f"Zammad connection test failed: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Test Failed',
                    'message': f'Connection error: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def create_ticket(self, title, body, customer_email, group_name="Users", priority="2 normal", state="new"):
        """Create a ticket in Zammad"""
        try:
            headers = {
                'Authorization': f'Token token={self.token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare ticket data
            ticket_data = {
                "title": title,
                "group": group_name,
                "customer": customer_email,
                "priority": priority,
                "state": state,
                "article": {
                    "subject": title,
                    "body": body,
                    "type": "note",
                    "internal": False
                }
            }
            
            _logger.info(f"Creating Zammad ticket: {ticket_data}")
            
            response = requests.post(
                f'{self.url}/api/v1/tickets',
                headers=headers,
                json=ticket_data,
                timeout=30
            )
            
            if response.status_code == 201:
                ticket_info = response.json()
                _logger.info(f"Zammad ticket created successfully: {ticket_info}")
                return {
                    'success': True,
                    'ticket_id': ticket_info.get('id'),
                    'ticket_number': ticket_info.get('number'),
                    'data': ticket_info
                }
            else:
                _logger.error(f"Failed to create Zammad ticket: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            _logger.error(f"Exception creating Zammad ticket: {e}")
            return {
                'success': False,
                'error': str(e)
            }
