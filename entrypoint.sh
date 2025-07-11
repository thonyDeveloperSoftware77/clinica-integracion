#!/bin/bash
# Instalar dependencias desde requirements.txt en custom_addons
for d in /mnt/extra-addons/*/ ; do
    if [ -f "$d/requirements.txt" ]; then
        pip install -r "$d/requirements.txt"
    fi
done
# Iniciar Odoo
exec odoo "$@"