import base64
import json
import logging
from datetime import datetime
from odoo import api, models
import requests

_logger = logging.getLogger(__name__)


class NextCloudService(models.AbstractModel):
    """Service for NextCloud integration"""
    _name = 'nextcloud.service'
    _description = 'NextCloud Service'

    @api.model
    def upload_prescription_pdf(self, prescription_record):
        """Upload prescription PDF to NextCloud"""
        try:
            # Generate PDF content
            pdf_content = self._generate_prescription_pdf(prescription_record)
            if not pdf_content:
                _logger.error(f'Failed to generate PDF for prescription {prescription_record.sequence_no}')
                return False
            
            # Upload to NextCloud
            success = self._upload_to_nextcloud(prescription_record, pdf_content)
            
            if success:
                _logger.info(f'Successfully uploaded prescription {prescription_record.sequence_no} to NextCloud')
                return True
            else:
                _logger.error(f'Failed to upload prescription {prescription_record.sequence_no} to NextCloud')
                return False
                
        except Exception as e:
            _logger.error(f'Error uploading prescription to NextCloud: {str(e)}')
            return False

    def _generate_prescription_pdf(self, prescription):
        """Generate PDF content for prescription"""
        try:
            # Create HTML content for the prescription
            html_content = self._create_prescription_html(prescription)
            
            # Try to use wkhtmltopdf if available, otherwise use simple text
            try:
                # For production, you would use wkhtmltopdf or similar
                # For now, we'll create a simple text representation
                pdf_content = self._create_simple_pdf_content(prescription)
                return pdf_content
            except Exception as e:
                _logger.warning(f'PDF generation fallback used: {str(e)}')
                return self._create_simple_pdf_content(prescription)
                
        except Exception as e:
            _logger.error(f'Error generating prescription PDF: {str(e)}')
            return None

    def _create_prescription_html(self, prescription):
        """Create HTML content for prescription"""
        patient_name = prescription.patient_id.name if prescription.patient_id else 'Unknown Patient'
        doctor_name = prescription.prescribed_doctor_id.name if prescription.prescribed_doctor_id else 'Unknown Doctor'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prescription {prescription.sequence_no}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                .content {{ margin: 20px 0; }}
                .footer {{ margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px; }}
                .field {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PRESCRIPTION</h1>
                <h2>Dental Hospital</h2>
            </div>
            
            <div class="content">
                <div class="field">
                    <span class="label">Prescription Reference:</span> {prescription.sequence_no}
                </div>
                <div class="field">
                    <span class="label">Patient:</span> {patient_name}
                </div>
                <div class="field">
                    <span class="label">Doctor:</span> {doctor_name}
                </div>
                <div class="field">
                    <span class="label">Date:</span> {prescription.create_date.strftime('%Y-%m-%d %H:%M') if prescription.create_date else 'N/A'}
                </div>
                <div class="field">
                    <span class="label">Appointment:</span> {prescription.appointment_id.appointment_no if prescription.appointment_id else 'N/A'}
                </div>
                
                <h3>Prescribed Medicines:</h3>
                <table border="1" cellpadding="5" cellspacing="0" style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f0f0f0;">
                        <th>Medicine</th>
                        <th>Generic Name</th>
                        <th>Form</th>
                        <th>Quantity</th>
                        <th>Schedule</th>
                        <th>Days</th>
                    </tr>"""
        
        # Add medicine lines
        if prescription.medicine_ids:
            for medicine in prescription.medicine_ids:
                schedule = []
                if medicine.morning:
                    schedule.append("Morning")
                if medicine.noon:
                    schedule.append("Afternoon")
                if medicine.night:
                    schedule.append("Night")
                schedule_text = ", ".join(schedule) or "Not specified"
                
                html_content += f"""
                    <tr>
                        <td>{medicine.medicament_id.name if medicine.medicament_id else 'N/A'}</td>
                        <td>{medicine.generic_name or 'N/A'}</td>
                        <td>{dict(medicine._fields['medicament_form'].selection).get(medicine.medicament_form, medicine.medicament_form) if medicine.medicament_form else 'N/A'}</td>
                        <td>{medicine.quantity}</td>
                        <td>{schedule_text} ({medicine.medicine_take if medicine.medicine_take else 'N/A'})</td>
                        <td>{medicine.days if medicine.days else 'N/A'}</td>
                    </tr>"""
        else:
            html_content += """
                    <tr>
                        <td colspan="6" style="text-align: center; font-style: italic;">No medicines prescribed</td>
                    </tr>"""
        
        html_content += f"""
                </table>
            </div>
            
            <div class="footer">
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Dental Hospital Management System</p>
            </div>
        </body>
        </html>
        """
        return html_content

    def _create_simple_pdf_content(self, prescription):
        """Create simple text-based PDF content"""
        patient_name = prescription.patient_id.name if prescription.patient_id else 'Unknown Patient'
        doctor_name = prescription.prescribed_doctor_id.name if prescription.prescribed_doctor_id else 'Unknown Doctor'
        
        content = f"""
DENTAL HOSPITAL - PRESCRIPTION
===============================

Prescription Reference: {prescription.sequence_no}
Patient: {patient_name}
Doctor: {doctor_name}
Date: {prescription.create_date.strftime('%Y-%m-%d %H:%M') if prescription.create_date else 'N/A'}
Appointment: {prescription.appointment_id.appointment_no if prescription.appointment_id else 'N/A'}

PRESCRIPTION DETAILS:
--------------------"""
        
        # Add medicine details
        if prescription.medicine_ids:
            for i, medicine in enumerate(prescription.medicine_ids, 1):
                schedule = []
                if medicine.morning:
                    schedule.append("Morning")
                if medicine.noon:
                    schedule.append("Afternoon")
                if medicine.night:
                    schedule.append("Night")
                schedule_text = ", ".join(schedule) or "Not specified"
                
                content += f"""
Medicine {i}:
  - Name: {medicine.medicament_id.name if medicine.medicament_id else 'N/A'}
  - Generic: {medicine.generic_name or 'N/A'}
  - Form: {medicine.medicament_form or 'N/A'}
  - Quantity: {medicine.quantity}
  - Schedule: {schedule_text} ({medicine.medicine_take if medicine.medicine_take else 'N/A'})
  - Days: {medicine.days if medicine.days else 'N/A'}
"""
        else:
            content += "\nNo medicines prescribed"
        
        content += f"""

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Dental Hospital Management System
        """
        
        # Convert to bytes for upload
        return content.encode('utf-8')

    def _upload_to_nextcloud(self, prescription, pdf_content):
        """Upload PDF to NextCloud via WebDAV"""
        try:
            # Get NextCloud configuration from system parameters
            config_param = self.env['ir.config_parameter'].sudo()
            nextcloud_url = config_param.get_param('nextcloud.url', 'http://nextcloud')
            nextcloud_port = config_param.get_param('nextcloud.port', '80')
            username = config_param.get_param('nextcloud.username', 'admin')
            password = config_param.get_param('nextcloud.password', 'admin_password75')
            base_folder = config_param.get_param('nextcloud.base_folder', 'Prescriptions')
            
            _logger.info(f'NextCloud config: URL={nextcloud_url}, Port={nextcloud_port}, User={username}, Folder={base_folder}')
            
            # Test basic connectivity to NextCloud
            try:
                test_response = requests.get(f"{nextcloud_url}/status.php", timeout=10)
                _logger.info(f'NextCloud status test: {test_response.status_code}')
            except Exception as conn_e:
                _logger.warning(f'NextCloud connectivity test failed: {str(conn_e)}')
            
            # Create organized folder structure
            patient_name = prescription.patient_id.name if prescription.patient_id else 'Unknown_Patient'
            # Clean patient name for file system
            patient_folder = self._clean_filename(patient_name)
            year = prescription.create_date.year if prescription.create_date else datetime.now().year
            month = prescription.create_date.month if prescription.create_date else datetime.now().month
            
            # Create folder path: /Prescriptions/YYYY/MM/Patient_Name/
            folder_path = f"{base_folder}/{year}/{month:02d}/{patient_folder}"
            
            # Create filename
            timestamp = prescription.create_date.strftime('%Y%m%d_%H%M%S') if prescription.create_date else datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prescription_{prescription.sequence_no}_{timestamp}.txt"
            
            # Full file path
            file_path = f"{folder_path}/{filename}"
            
            _logger.info(f'Creating file path: {file_path}')
            
            # Create directories first
            self._create_nextcloud_directories(nextcloud_url, username, password, folder_path)
            
            # Upload file
            upload_url = f"{nextcloud_url}/remote.php/dav/files/{username}/{file_path}"
            
            _logger.info(f'Upload URL: {upload_url}')
            
            headers = {
                'Content-Type': 'text/plain',
            }
            
            auth = (username, password)
            
            response = requests.put(
                upload_url,
                data=pdf_content,
                headers=headers,
                auth=auth,
                timeout=30
            )
            
            _logger.info(f'Upload response: Status={response.status_code}')
            
            if response.status_code in [200, 201, 204]:
                _logger.info(f'Successfully uploaded prescription to NextCloud: {file_path}')
                
                # Store the NextCloud path in the prescription record
                prescription.nextcloud_file_path = file_path
                prescription.nextcloud_upload_status = 'success'
                
                return True
            else:
                _logger.error(f'Failed to upload to NextCloud. Status: {response.status_code}')
                _logger.error(f'Response headers: {dict(response.headers)}')
                _logger.error(f'Response content (first 1000 chars): {response.text[:1000]}')
                
                prescription.nextcloud_upload_status = 'failed'
                return False
                
        except Exception as e:
            _logger.error(f'Error uploading to NextCloud: {str(e)}')
            prescription.nextcloud_upload_status = 'failed'
            return False

    def _create_nextcloud_directories(self, base_url, username, password, folder_path):
        """Create directory structure in NextCloud"""
        try:
            auth = (username, password)
            
            # Split path and create each directory
            path_parts = folder_path.split('/')
            current_path = ''
            
            for part in path_parts:
                if part:  # Skip empty parts
                    current_path += f'/{part}' if current_path else part
                    
                    # Try to create directory
                    dir_url = f"{base_url}/remote.php/dav/files/{username}/{current_path}"
                    
                    response = requests.request(
                        'MKCOL',
                        dir_url,
                        auth=auth,
                        timeout=10
                    )
                    
                    # 201 = created, 405 = already exists
                    if response.status_code not in [201, 405]:
                        _logger.warning(f'Could not create directory {current_path}: {response.status_code}')
                        
        except Exception as e:
            _logger.warning(f'Error creating directories in NextCloud: {str(e)}')

    def _clean_filename(self, filename):
        """Clean filename for file system compatibility"""
        import re
        # Replace invalid characters with underscores
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove multiple underscores and spaces
        cleaned = re.sub(r'[_\s]+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        return cleaned or 'Unknown'

    @api.model
    def test_nextcloud_connection(self):
        """Test connection to NextCloud"""
        try:
            # Get configuration from system parameters
            config_param = self.env['ir.config_parameter'].sudo()
            nextcloud_url = config_param.get_param('nextcloud.url', 'http://nextcloud')
            username = config_param.get_param('nextcloud.username', 'admin')
            password = config_param.get_param('nextcloud.password', 'admin_password75')
            
            test_url = f"{nextcloud_url}/remote.php/dav/files/{username}/"
            
            auth = (username, password)
            
            response = requests.request(
                'PROPFIND',
                test_url,
                auth=auth,
                timeout=10
            )
            
            if response.status_code in [200, 207]:  # 207 = Multi-Status (WebDAV success)
                return True, "NextCloud connection successful"
            else:
                return False, f"NextCloud connection failed: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"NextCloud connection error: {str(e)}"
