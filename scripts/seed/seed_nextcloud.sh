#!/usr/bin/env bash
curl -u admin:${NEXTCLOUD_ADMIN_PASSWORD:-admin123} \
     -T ejemplo.pdf \
     http://localhost:8081/remote.php/dav/files/admin/ejemplo.pdf
echo "Subido ejemplo.pdf"
