from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import email_normalize
from datetime import date
import re


class DentalPatients(models.Model):
    """To create Patients in the clinic, use res.partner model and customize it"""
    _inherit = 'res.partner'

    patient_no = fields.Char(string='Patient No.', copy=False, index=True)  # Ensure uniqueness
    is_patient = fields.Boolean(string="Is a Patient", default=False)  # New field to identify patients

    company_type = fields.Selection(selection_add=[('person', 'Patient'),
                                                   ('company', 'Medicine Distributor')],
                                    help="Patient type")

    dob = fields.Date(string="Date of Birth",
                      help="DOB of the patient")
    patient_age = fields.Integer(compute='_compute_patient_age',
                                 store=True,
                                 string="Age",
                                 help="Age of the patient")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              string="gender",
                              help="gender of the patient")
    medical_questionnaire_ids = fields.One2many('medical.questionnaire',
                                                'patient_id',
                                                readonly=False,
                                                help="connect model medical questionnaire in patients")
    report_ids = fields.One2many('xray.report', 'patient_id',
                                 string='X-Ray',
                                 help="To add the xray reports of the patient")

    @api.depends('complete_name', 'email', 'vat', 'state_id', 'country_id', 'commercial_company_name', 'patient_no')
    @api.depends_context('show_address', 'partner_show_db_id', 'address_inline', 'show_email', 'show_vat', 'lang')
    def _compute_display_name(self):
        for partner in self:
            name = partner.with_context(lang=self.env.lang)._get_complete_name()

            # Include Patient No if available
            if partner.patient_no:
                name = f" {partner.patient_no} - {name}"

            if partner._context.get('show_address'):
                name = name + "\n" + partner._display_address(without_company=True)

            name = re.sub(r'\s+\n', '\n', name)

            if partner._context.get('partner_show_db_id'):
                name = f"{name} ({partner.id})"

            if partner._context.get('address_inline'):
                splitted_names = name.split("\n")
                name = ", ".join([n for n in splitted_names if n.strip()])

            if partner._context.get('show_email') and partner.email:
                name = f"{name} <{partner.email}>"

            if partner._context.get('show_vat') and partner.vat:
                name = f"{name} ‒ {partner.vat}"

            partner.display_name = name.strip()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ Search by both patient name and patient_no. """
        args = args or []
        if name:
            args += ['|', ('name', operator, name), ('patient_no', operator, name)]
        return super(DentalPatients, self).name_search(name, args, operator, limit)

    @api.model_create_multi
    def create(self, vals_list):
        """ Generate a unique patient number if not already assigned """
        records = super(DentalPatients, self).create(vals_list)

        for record in records:
            if record.is_patient and not record.patient_no:
                patient_no = self.env['ir.sequence'].next_by_code('dental.patient') or 'PAT/NEW'
                record.write({'patient_no': patient_no})  # Ensure value is saved

        return records

    @api.depends('dob')
    def _compute_patient_age(self):
        """Safely computes age, avoiding NoneType errors"""
        today = date.today()
        for record in self:
            if record.dob:
                dob = record.dob
                record.patient_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                record.patient_age = 0


    def action_prescription(self):
        """Open existing prescriptions in list view or create a new one with auto-filled values."""
        self.ensure_one()
        Prescription = self.env['dental.prescription']

        # Search for all existing prescriptions for this patient
        prescriptions = Prescription.search([('patient_id', '=', self.id)])
        # Fetch selected teeth from the latest Teeth Chart for this patient
        teeth_chart = self.env['teeth.chart'].search([('name', '=', self.name)], order='id desc', limit=1)
        selected_teeth = teeth_chart.selected_teeth if teeth_chart else "None"

        # Get the latest created appointment for this patient (not just by date, but by record ID)
        appointment = self.env['dental.appointment'].search(
            [('patient_id', '=', self.id)], order='id desc', limit=1
            # ORDER BY ID DESC to get the most recently created appointment
        )
        # Check if there are existing prescriptions
        prescriptions = Prescription.search([('patient_id', '=', self.id)])

        if prescriptions:
            # Open list view of prescriptions if there are existing ones
            return {
                'type': 'ir.actions.act_window',
                'name': 'Prescriptions',
                'view_mode': 'list,form',
                'res_model': 'dental.prescription',
                'domain': [('id', 'in', prescriptions.ids)],  # Show only this patient's prescriptions
                'target': 'current',
                'context': {
                    'default_patient_id': self.id,
                    'default_appointment_id': appointment.id if appointment else False,
                    'default_prescription_date': fields.Date.today(),
                    'default_prescribed_doctor_id': appointment.dentist_id.id if appointment and appointment.dentist_id else self.env.user.id,
                    'default_state': 'new',
                    'default_selected_teeth': selected_teeth,
                }
            }
        else:
            # Create a new prescription if none exists
            prescription = Prescription.create({
                'patient_id': self.id,
                'appointment_id': appointment.id if appointment else False,
                'prescription_date': fields.Date.today(),
                'prescribed_doctor_id': appointment.dentist_id.id if appointment and appointment.dentist_id else self.env.user.id,
                'state': 'new',
                'selected_teeth': selected_teeth,
            })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Prescription',
                'view_mode': 'form',
                'res_model': 'dental.prescription',
                'res_id': prescription.id,
                'target': 'current',
            }

    def action_teeth_chart(self):
        """Open the Teeth Chart form with patient details pre-filled."""
        self.ensure_one()

        # Check if a teeth chart record already exists for the patient
        teeth_chart = self.env['teeth.chart'].search([('name', '=', self.name)], limit=1)

        if teeth_chart:
            # Open the existing teeth chart
            return {
                'type': 'ir.actions.act_window',
                'target': 'current',
                'name': 'Teeth Chart',
                'view_mode': 'form',
                'res_model': 'teeth.chart',
                'res_id': teeth_chart.id,
            }
        else:
            # Create a new teeth chart with patient name auto-filled
            teeth_chart = self.env['teeth.chart'].create({
                'name': self.name,
            })
            return {
                'type': 'ir.actions.act_window',
                'target': 'current',
                'name': 'Teeth Chart',
                'view_mode': 'form',
                'res_model': 'teeth.chart',
                'res_id': teeth_chart.id,
            }

    def action_open_patient_payments(self):
        """Open all account.payment records for this patient."""
        self.ensure_one()
        treatment_name = self.env.context.get('default_treatment_name')
        treatment_cost = self.env.context.get('default_treatment_cost')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Payments',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'search_default_partner_id': self.id,
                'default_treatment_name': treatment_name,
                'default_treatment_cost': treatment_cost,
            },
            'target': 'current',
        }