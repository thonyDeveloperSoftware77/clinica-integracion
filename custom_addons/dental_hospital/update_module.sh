#!/bin/bash
# Script to update the dental_hospital module

echo "=== Updating dental_hospital module ==="

# Change to the Odoo directory
cd /opt/odoo

# Update the module
sudo -u odoo ./odoo-bin -u dental_hospital -d odoo_db --stop-after-init

echo "=== Module updated successfully ==="
