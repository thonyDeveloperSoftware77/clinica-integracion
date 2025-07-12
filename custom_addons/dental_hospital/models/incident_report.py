from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
import logging
import re
from datetime import datetime

_logger = logging.getLogger(__name__)


class IncidentReport(models.Model):
    """Simple incident report model"""
    _name = 'incident.report'
    _description = 'Incident Report'
    _order = 'create_date desc'

    name = fields.Char(string='Reference', default='New', readonly=True)
    description = fields.Text(string='Incident Description', required=True)
    priority = fields.Selection([
        ('normal', 'Normal'),
        ('alto', 'Alto'),
        ('critico', 'Crítico')
    ], string='Priority', default='normal', required=True)
    user_name = fields.Char(string='Reported by', readonly=True)
    user_email = fields.Char(string='Email', readonly=True)
    zammad_ticket_number = fields.Char(string='Zammad Ticket', readonly=True)
    zammad_ticket_id = fields.Integer(string='Zammad Ticket ID', readonly=True)
    zammad_responses = fields.Text(string='Conversation History', readonly=True)
    new_response = fields.Text(string='Add Response')
    last_sync = fields.Datetime(string='Last Sync', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent to Zammad'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed')
    ], string='Status', default='draft', readonly=True)
    can_respond = fields.Boolean(string='Can Respond', compute='_compute_can_respond')
    
    @api.depends('state')
    def _compute_can_respond(self):
        """Compute if user can respond to ticket"""
        for record in self:
            record.can_respond = record.state != 'closed' and record.zammad_ticket_id
    
    @api.model
    def create(self, vals):
        """Auto-assign sequence number and current user info"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('incident.report') or 'New'
        
        # Get current user info from Clerk context
        current_user = self.env.user
        vals['user_name'] = current_user.name
        vals['user_email'] = current_user.email
        
        if not vals['user_email']:
            raise UserError(_('User email is required to create incident reports'))
        
        # Create the record first
        record = super(IncidentReport, self).create(vals)
        
        # Automatically send to Zammad after creation
        try:
            record._send_to_zammad_auto()
        except Exception as e:
            _logger.error(f'Failed to auto-send to Zammad: {str(e)}')
            # Don't fail the creation if Zammad fails, just log it
        
        return record
    
    @api.model
    def default_get(self, fields_list):
        """Set default user info based on current user"""
        defaults = super(IncidentReport, self).default_get(fields_list)
        current_user = self.env.user
        
        if 'user_name' in fields_list:
            defaults['user_name'] = current_user.name
        if 'user_email' in fields_list:
            defaults['user_email'] = current_user.email
            
        return defaults
    
    def _send_to_zammad_auto(self):
        """Send to Zammad automatically (internal method)"""
        self.ensure_one()
        
        # URL de Zammad usando localhost (ya que está expuesto en el puerto 8080)
        zammad_url = 'http://172.17.0.1:8080'  # IP del host Docker
        
        # Token de Zammad (fijo)
        zammad_token = 'yYXUM8mJauxf74j5SaV0EPu7H-4ZhYRZUGSyfJ91rDqvMSfVUw_hIa33isD8TJR2'
        
        # Preparar headers con token de Zammad
        headers = {
            'Authorization': f'Token token={zammad_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Use user info from the record
            user_name = self.user_name
            user_email = self.user_email
            
            # Datos del ticket según documentación de Zammad
            ticket_data = {
                'title': f'Incident Report - {self.name}',
                'customer_id': f'guess:{user_email}',  # Auto-create customer
                'group_id': 1,  # ID del grupo Users
                'article': {
                    'subject': f'Incident Report - {self.name}',
                    'body': f"Reported by: {user_name} ({user_email})\n\nDescription:\n{self.description}",
                    'type': 'note',
                    'internal': False
                }
            }
            
            response = requests.post(
                f'{zammad_url}/api/v1/tickets',
                headers=headers,
                json=ticket_data,
                timeout=30
            )
            
            if response.status_code == 201:
                ticket_response = response.json()
                self.zammad_ticket_number = ticket_response.get('number')
                self.zammad_ticket_id = ticket_response.get('id')
                self.state = 'sent'
                _logger.info(f'Ticket created automatically: {self.zammad_ticket_number} (ID: {self.zammad_ticket_id})')
            else:
                error_msg = f'Status: {response.status_code}, Response: {response.text}'
                _logger.error(f'Failed to create Zammad ticket: {error_msg}')
                
        except Exception as e:
            _logger.error(f'Error auto-sending to Zammad: {str(e)}')
            raise

    def action_send_to_zammad(self):
        """Send to Zammad manually (for backwards compatibility)"""
        self._send_to_zammad_auto()
        
        if self.zammad_ticket_number:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Incident sent to Zammad. Ticket #%s') % self.zammad_ticket_number,
                    'type': 'success'
                }
            }
        else:
            raise UserError(_('Failed to send to Zammad. Check logs for details.'))
    
    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """Filter incidents to show only current user's reports"""
        # Get current user email
        current_user = self.env.user
        if current_user.email:
            # Add domain filter for current user's email
            domain = domain + [('user_email', '=', current_user.email)]
        else:
            # If no email, show no records (security measure)
            domain = domain + [('id', '=', False)]
        
        return super(IncidentReport, self).search(domain, offset, limit, order, count)

    def sync_zammad_responses(self):
        """Sync responses from Zammad ticket"""
        self.ensure_one()
        
        if not self.zammad_ticket_id:
            return
        
        # URL de Zammad y token
        zammad_url = 'http://172.17.0.1:8080'
        zammad_token = 'yYXUM8mJauxf74j5SaV0EPu7H-4ZhYRZUGSyfJ91rDqvMSfVUw_hIa33isD8TJR2'
        
        headers = {
            'Authorization': f'Token token={zammad_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Get ticket details
            ticket_response = requests.get(
                f'{zammad_url}/api/v1/tickets/{self.zammad_ticket_id}',
                headers=headers,
                timeout=30
            )
            
            if ticket_response.status_code == 200:
                ticket_data = ticket_response.json()
                
                # Map state_id to state name and then to our state
                state_id_mapping = {
                    1: 'new',
                    2: 'open', 
                    3: 'pending reminder',
                    4: 'closed',
                    5: 'merged',
                    6: 'pending close'
                }
                
                state_mapping = {
                    'new': 'sent',
                    'open': 'in_progress',
                    'pending reminder': 'in_progress',
                    'pending close': 'in_progress',
                    'closed': 'closed',
                    'merged': 'closed'
                }
                
                zammad_state_id = ticket_data.get('state_id', 1)
                zammad_state_name = state_id_mapping.get(zammad_state_id, 'new')
                new_state = state_mapping.get(zammad_state_name, 'sent')
                
                # Get articles (responses)
                articles_response = requests.get(
                    f'{zammad_url}/api/v1/ticket_articles/by_ticket/{self.zammad_ticket_id}',
                    headers=headers,
                    timeout=30
                )
                
                if articles_response.status_code == 200:
                    articles = articles_response.json()
                    
                    # Format responses
                    formatted_responses = []
                    for article in articles:
                        article_type = article.get('type', 'note')
                        sender_type = article.get('sender', 'Agent')
                        is_internal = article.get('internal', False)
                        
                        # Only show non-internal articles
                        if not is_internal and article_type in ['note', 'web', 'email']:
                            sender = article.get('from', 'Unknown')
                            created_at = article.get('created_at', '')
                            body = article.get('body', '')
                            
                            # Format the date
                            try:
                                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                formatted_date = created_at
                            
                            # Clean HTML from body if present
                            if article.get('content_type') == 'text/html':
                                body_clean = re.sub(r'<[^>]+>', '', body)
                                body_clean = body_clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip()
                            else:
                                body_clean = body.strip()
                            
                            if body_clean:  # Only add non-empty messages
                                sender_display = f"{sender} ({sender_type})"
                                formatted_responses.append(
                                    f"=== {sender_display} - {formatted_date} ===\n{body_clean}\n"
                                )
                    
                    # Update record
                    self.write({
                        'zammad_responses': '\n'.join(formatted_responses) if formatted_responses else 'No responses yet.',
                        'state': new_state,
                        'last_sync': fields.Datetime.now()
                    })
                    
                    _logger.info(f'Synced responses for ticket {self.zammad_ticket_number} - State: {zammad_state_name} -> {new_state}')
                    
        except Exception as e:
            _logger.error(f'Error syncing Zammad responses: {str(e)}')
            raise
    
    def action_sync_responses(self):
        """Manual sync action for responses"""
        try:
            old_responses = self.zammad_responses
            old_state = self.state
            
            self.sync_zammad_responses()
            
            # Check if anything changed
            if old_responses != self.zammad_responses or old_state != self.state:
                _logger.info(f'Sync successful for ticket {self.zammad_ticket_number}. State: {old_state} -> {self.state}')
                
                # Return action to reload the form view
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'incident.report',
                    'res_id': self.id,
                    'view_mode': 'form',
                    'target': 'current',
                    'context': dict(self.env.context)
                }
            else:
                _logger.info(f'No changes detected for ticket {self.zammad_ticket_number}')
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Sync Complete'),
                        'message': _('No new changes found'),
                        'type': 'info'
                    }
                }
        except Exception as e:
            _logger.error(f'Error in manual sync: {str(e)}')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Error'),
                    'message': _('Failed to sync conversation: %s') % str(e),
                    'type': 'danger'
                }
            }

    def action_send_response(self):
        """Send new response to Zammad"""
        self.ensure_one()
        
        if not self.new_response or not self.new_response.strip():
            raise UserError(_('Please enter a response before sending.'))
        
        if not self.zammad_ticket_id:
            raise UserError(_('No Zammad ticket associated with this incident.'))
        
        if self.state == 'closed':
            raise UserError(_('Cannot respond to a closed ticket.'))
        
        # URL de Zammad y token
        zammad_url = 'http://172.17.0.1:8080'
        zammad_token = 'yYXUM8mJauxf74j5SaV0EPu7H-4ZhYRZUGSyfJ91rDqvMSfVUw_hIa33isD8TJR2'
        
        headers = {
            'Authorization': f'Token token={zammad_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Send article (response) to Zammad
            article_data = {
                'ticket_id': self.zammad_ticket_id,
                'subject': f'Re: {self.name}',
                'body': self.new_response,
                'type': 'web',
                'internal': False,
                'from': self.user_email or 'Unknown'
            }
            
            _logger.info(f'Sending response to Zammad ticket {self.zammad_ticket_number}: {article_data}')
            
            response = requests.post(
                f'{zammad_url}/api/v1/ticket_articles',
                headers=headers,
                json=article_data,
                timeout=30
            )
            
            _logger.info(f'Zammad response status: {response.status_code}, body: {response.text}')
            
            if response.status_code == 201:
                # Clear the response field
                self.new_response = ''
                
                # Sync responses to get the updated conversation
                self.sync_zammad_responses()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Response Sent'),
                        'message': _('Your response has been sent successfully'),
                        'type': 'success'
                    }
                }
            else:
                error_msg = f'Status: {response.status_code}, Response: {response.text}'
                _logger.error(f'Failed to send response to Zammad: {error_msg}')
                raise UserError(_('Failed to send response to Zammad: %s') % error_msg)
                
        except Exception as e:
            _logger.error(f'Error sending response to Zammad: {str(e)}')
            raise UserError(_('Error sending response: %s') % str(e))
    
    def _get_zammad_config(self):
        """Get Zammad configuration"""
        return {
            'url': 'http://172.17.0.1:8080',
            'token': 'yYXUM8mJauxf74j5SaV0EPu7H-4ZhYRZUGSyfJ91rDqvMSfVUw_hIa33isD8TJR2',
            'headers': {
                'Authorization': f'Token token=yYXUM8mJauxf74j5SaV0EPu7H-4ZhYRZUGSyfJ91rDqvMSfVUw_hIa33isD8TJR2',
                'Content-Type': 'application/json'
            }
        }
    
    def test_zammad_connection(self):
        """Test connection to Zammad"""
        config = self._get_zammad_config()
        try:
            response = requests.get(
                f"{config['url']}/api/v1/tickets",
                headers=config['headers'],
                timeout=10
            )
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
