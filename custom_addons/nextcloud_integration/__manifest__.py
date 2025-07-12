{
    'name': 'NextCloud Integration',
    'version': '1.0.0',
    'category': 'Integration',
    'summary': 'NextCloud integration for automatic PDF upload',
    'description': """
        This module provides NextCloud integration to automatically upload
        prescription PDFs when dental prescriptions are created.
        
        Features:
        - Automatic PDF generation for prescriptions
        - Upload to NextCloud with organized folder structure
        - WebDAV integration with NextCloud
    """,
    'author': 'Your Company',
    'depends': ['base', 'dental_hospital'],
    'data': [
        'data/ir_config_parameter.xml',
        'views/dental_prescription_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
