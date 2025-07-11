{
    'name': 'Zammad Integration',
    'version': '1.0',
    'depends': ['base', 'project', 'mail'],
    'author': 'Clinica Integration',
    'category': 'Integration',
    'description': """
        Integration module for Zammad ticketing system.
        Allows creating tickets in Zammad from Odoo.
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/zammad_config_views.xml',
        'views/ticket_views.xml',
        'data/zammad_config_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
