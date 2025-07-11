from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campos personalizados para pacientes
    is_patient = fields.Boolean(string="Is Patient", default=False)
    dob = fields.Date(string="Date of Birth")
    patient_age = fields.Integer(string="Age")
    patient_no = fields.Char(string="Patient No.")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    # Si quieres los del cuestionario:
    # medical_questionnaire_ids = fields.One2many('dental.medical.questionnaire', 'partner_id', string='Medical Questionnaire')
    # report_ids = fields.One2many('dental.xray.report', 'partner_id', string='X-Ray Reports')
