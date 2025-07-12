{
    'name': 'RabbitMQ Integration',
    'version': '1.0',
    'summary': 'Integration with RabbitMQ for incident reports',
    'description': '''
        This module provides RabbitMQ integration functionality
        for sending incident report notifications.
    ''',
    'author': 'Clinica Team',
    'depends': ['base', 'dental_hospital'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['pika'],
    },
}
