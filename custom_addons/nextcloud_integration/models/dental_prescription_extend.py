from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class DentalPrescriptionExtend(models.Model):
    """Extend dental prescription model to add NextCloud integration"""
    _inherit = 'dental.prescription'

    nextcloud_file_path = fields.Char(
        string='NextCloud File Path',
        readonly=True,
        help='Path to the prescription file in NextCloud'
    )
    
    nextcloud_upload_status = fields.Selection([
        ('pending', 'Pending Upload'),
        ('uploading', 'Uploading'),
        ('success', 'Upload Successful'),
        ('failed', 'Upload Failed')
    ], string='NextCloud Status', default='pending', readonly=True)

    @api.model
    def create(self, vals):
        """Override create to add NextCloud upload"""
        # Call original create method
        record = super(DentalPrescriptionExtend, self).create(vals)
        
        # Upload prescription to NextCloud after successful creation
        try:
            record.nextcloud_upload_status = 'uploading'
            self._upload_prescription_to_nextcloud(record)
        except Exception as e:
            _logger.error(f'Failed to upload prescription to NextCloud: {str(e)}')
            record.nextcloud_upload_status = 'failed'
            # Don't fail the creation if NextCloud upload fails
        
        return record
    
    def _upload_prescription_to_nextcloud(self, record):
        """Upload prescription to NextCloud"""
        # Get NextCloud service
        nextcloud_service = self.env['nextcloud.service']
        
        # Upload prescription PDF
        success = nextcloud_service.upload_prescription_pdf(record)
        
        if success:
            record.nextcloud_upload_status = 'success'
            _logger.info(f'Prescription {record.sequence_no} uploaded to NextCloud successfully')
        else:
            record.nextcloud_upload_status = 'failed'
            _logger.warning(f'Failed to upload prescription {record.sequence_no} to NextCloud')

    def action_reupload_to_nextcloud(self):
        """Manual action to re-upload prescription to NextCloud"""
        self.ensure_one()
        
        try:
            self.nextcloud_upload_status = 'uploading'
            self._upload_prescription_to_nextcloud(self)
            
            if self.nextcloud_upload_status == 'success':
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Prescription uploaded to NextCloud successfully'),
                        'type': 'success'
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': _('Failed to upload prescription to NextCloud'),
                        'type': 'danger'
                    }
                }
        except Exception as e:
            self.nextcloud_upload_status = 'failed'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Error uploading to NextCloud: %s') % str(e),
                    'type': 'danger'
                }
            }

    def action_view_nextcloud_file(self):
        """Open NextCloud file in browser"""
        self.ensure_one()
        
        if not self.nextcloud_file_path:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No File'),
                    'message': _('No file has been uploaded to NextCloud yet'),
                    'type': 'warning'
                }
            }
        
        # Construct NextCloud file URL
        nextcloud_base_url = 'http://localhost:8082'  # External access URL
        file_url = f"{nextcloud_base_url}/f/{self.nextcloud_file_path.replace('/', '%2F')}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': file_url,
            'target': 'new',
        }
