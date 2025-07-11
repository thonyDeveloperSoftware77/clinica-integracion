from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError


class IncidentPortal(http.Controller):

    @http.route(['/my/incidents'], type='http', auth="user", website=True)
    def portal_my_incidents(self, **kw):
        """Simple incidents list for portal users"""
        try:
            # Get incidents for current user
            incidents = request.env['incident.report'].search([
                ('patient_id.user_ids', 'in', [request.env.user.id])
            ])
            
            values = {
                'incidents': incidents,
                'page_name': 'incident',
            }
            
            return request.render("dental_hospital.portal_my_incidents", values)
        except Exception as e:
            return request.redirect('/my')
