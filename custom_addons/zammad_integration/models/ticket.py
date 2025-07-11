from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Ticket(models.Model):
    _name = 'zammad.ticket'
    _description = 'Support Ticket'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Subject', required=True)
    description = fields.Text('Description')
    partner_id = fields.Many2one('res.partner', 'Customer')
    partner_email = fields.Char('Customer Email')
    user_id = fields.Many2one('res.users', 'Assigned To')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'), 
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], default='new', required=True)
    priority = fields.Selection([
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High'),
        ('4', 'Urgent')
    ], default='2', required=True)
    
    # Zammad integration fields
    zammad_ticket_id = fields.Char('Zammad Ticket ID', readonly=True)
    zammad_ticket_number = fields.Char('Zammad Ticket Number', readonly=True)
    zammad_url = fields.Char('Zammad URL', readonly=True)
    sync_to_zammad = fields.Boolean('Sync to Zammad', default=False)
    
    @api.depends('partner_id')
    def _compute_partner_email(self):
        for ticket in self:
            ticket.partner_email = ticket.partner_id.email if ticket.partner_id else ''
    
    def create_zammad_ticket(self):
        """Create ticket in Zammad"""
        if self.zammad_ticket_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Already Synced',
                    'message': f'This ticket is already synced to Zammad (#{self.zammad_ticket_number})',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        try:
            # Get Zammad configuration
            config = self.env['zammad.config'].get_active_config()
            
            # Prepare ticket data
            customer_email = self.partner_email or (self.partner_id.email if self.partner_id else 'no-reply@example.com')
            title = self.name or 'Ticket from Odoo'
            body = self.description or 'No description provided'
            
            # Map priority
            priority_map = {
                '1': '1 low',
                '2': '2 normal', 
                '3': '3 high',
                '4': '4 urgent'
            }
            priority = priority_map.get(self.priority, '2 normal')
            
            # Create ticket in Zammad
            result = config.create_ticket(
                title=title,
                body=body,
                customer_email=customer_email,
                group_name="Users",
                priority=priority
            )
            
            if result.get('success'):
                # Update Odoo ticket with Zammad info
                self.write({
                    'zammad_ticket_id': result['ticket_id'],
                    'zammad_ticket_number': result['ticket_number'],
                    'zammad_url': f"{config.url}/ticket/zoom/{result['ticket_id']}",
                    'sync_to_zammad': True
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Zammad Ticket Created',
                        'message': f'Ticket #{result["ticket_number"]} created successfully in Zammad',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Zammad Sync Failed',
                        'message': f'Failed to create Zammad ticket: {result.get("error", "Unknown error")}',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
                
        except Exception as e:
            _logger.error(f"Error creating Zammad ticket: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Error creating Zammad ticket: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def open_zammad_ticket(self):
        """Open the Zammad ticket in browser"""
        if not self.zammad_url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Zammad Ticket',
                    'message': 'This ticket is not synced to Zammad',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.zammad_url,
            'target': 'new',
        }
