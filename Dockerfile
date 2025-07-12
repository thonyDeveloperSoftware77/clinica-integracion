FROM odoo:18

# Ejecutar como root para instalar dependencias
USER root

# Instalar python-jose, requests y pika usando --break-system-packages (necesario para Python 3.12+)
RUN pip3 install --no-cache-dir --break-system-packages python-jose requests pika

# Volver al usuario por defecto de Odoo
USER odoo

# Comando por defecto
CMD ["odoo"]