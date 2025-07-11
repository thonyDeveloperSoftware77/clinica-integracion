# -*- coding: utf-8 -*-

import datetime
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DentalPrescription(models.Model):
    """Prescription of patient from the dental clinic"""
    _name = 'dental.prescription'
    _description = "Dental Prescription"
    _inherit = ['mail.thread']
    _rec_name = "sequence_no"

    sequence_no = fields.Char(string='Sequence No', required=True,
                              readonly=True, default=lambda self: _('New'),
                              help="Sequence number of the dental prescription")
    appointment_ids = fields.Many2many('dental.appointment',
                                       string="Available Appointments",
                                       compute="_compute_appointment_ids",
                                       store=False,
                                       help="All available appointments for selection")
    appointment_id = fields.Many2one('dental.appointment',
                                     string="Appointment",
                                     required=True,
                                     help="Select from available appointments (recent past, today, and future)")
    patient_id = fields.Many2one('res.partner',
                                 string="Patient",
                                 required=True,
                                 domain="[('is_patient', '=', True)]",
                                 help="name of the patient")
    # token_no = fields.Integer(related="appointment_id.token_no",
    #                           string="Token Number",
    #                           help="Token number of the patient")
    treatment_id = fields.Many2one('dental.treatment',
                                   string="Treatment",
                                   help="Name of the treatment done for patient")
    cost = fields.Float(related="treatment_id.cost",
                        string="Treatment Cost",
                        help="Cost of treatment")
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id,
                                  required=True,
                                  help="To add the currency type in cost")
    prescribed_doctor_id = fields.Many2one('hr.employee',
                                           string='Prescribed Doctor',
                                           required=True,
                                           domain="[('is_dentist', '=', True)]",
                                           help="Doctor who is prescribed")
    prescription_date = fields.Date(default=fields.date.today(),
                                    string='Prescription Date',
                                    required=True,
                                    help="Date of the prescription")
    state = fields.Selection([('new', 'New'),
                              ('done', 'Prescribed'),
                              ('invoiced', 'Invoiced')],
                             default="new",
                             string="state",
                             help="state of the appointment")
    medicine_ids = fields.One2many('dental.prescription_lines',
                                   'prescription_id',
                                   string="Medicine",
                                   help="medicines")
    invoice_data_id = fields.Many2one(comodel_name="account.move", string="Invoice Data",
                                      help="Invoice Data")
    treatment_invoice_id = fields.Many2one('account.move', string="Treatment Invoice")
    prescription_invoice_id = fields.Many2one('account.move', string="Prescription Invoice")
    selected_teeth = fields.Char(string="Selected Teeth",help="Selected Teeth")
    referred_dentist_id = fields.Many2one(
        'hr.employee', string='Referred Dentist',
        domain="[('is_dentist', '=', True)]",
        help="Select a different dentist if referring the patient"
    )
    next_appointment_date = fields.Date(
        string="Next Appointment Date",
        help="Date for the next appointment"
    )
    # grand_total = fields.Float(compute="_compute_grand_total",
    #                            string="Grand Total",
    #                            help="Get the grand total amount")

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure the next appointment is updated/created when a prescription is created."""
        for vals in vals_list:
            if vals.get('sequence_no', _('New')) == _('New'):
                vals['sequence_no'] = self.env['ir.sequence'].next_by_code('dental.prescriptions') or _('New')
        
        records = super(DentalPrescription, self).create(vals_list)
        
        for record in records:
            # Force computation of appointment_ids after creation
            record._compute_appointment_ids()
            record._update_or_create_appointment()
        
        return records

    def write(self, vals):
        """Ensure the next appointment is updated when a prescription is modified."""
        res = super(DentalPrescription, self).write(vals)
        if 'next_appointment_date' in vals or 'referred_dentist_id' in vals:
            for record in self:
                record._update_or_create_appointment()
        return res

    def _update_or_create_appointment(self):
        """Creates a new appointment instead of modifying the current one."""
        if not self.next_appointment_date or not self.patient_id:
            return  # Skip if no next appointment date is given

        assigned_dentist = self.referred_dentist_id or self.prescribed_doctor_id
        if not assigned_dentist:
            return  # Skip if no doctor is assigned

        today_appointment = self.env['dental.appointment'].search([
            ('patient_id', '=', self.patient_id.id),
            ('appointment_date', '=', fields.Date.today()),
            ('state', '!=', 'done')
        ], limit=1)

        # Ensure that today's appointment is not modified
        if today_appointment:
            # Create a new appointment for the next visit
            self.env['dental.appointment'].create({
                'patient_id': self.patient_id.id,
                'appointment_date': self.next_appointment_date,
                'dentist_id': assigned_dentist.id,
                'state': 'draft',  # Set as draft since it's a future appointment
            })
        else:
            # If no active appointment exists today, update or create as usual
            upcoming_appointment = self.env['dental.appointment'].search([
                ('patient_id', '=', self.patient_id.id),
                ('appointment_date', '>', fields.Date.today()),
                ('state', '!=', 'done')
            ], limit=1, order="appointment_date asc")

            if upcoming_appointment:
                upcoming_appointment.write({
                    'appointment_date': self.next_appointment_date,
                    'dentist_id': assigned_dentist.id
                })
            else:
                # Create a new future appointment
                self.env['dental.appointment'].create({
                    'patient_id': self.patient_id.id,
                    'appointment_date': self.next_appointment_date,
                    'dentist_id': assigned_dentist.id,
                    'state': 'draft',
                })

    @api.depends('patient_id')
    def _compute_appointment_ids(self):
        """Computes and assigns the `appointment_ids` field for each record.
        This method searches for all `dental.appointment` records that are
        available for prescription (not cancelled). It shows appointments
        from the last 30 days and future appointments to allow prescriptions
        for completed appointments and upcoming ones."""
        import logging
        _logger = logging.getLogger(__name__)
        
        for rec in self:
            # Base domain: exclude cancelled appointments
            domain = [('state', '!=', 'cancelled')]
            
            # If a patient is already selected, filter by patient
            if rec.patient_id:
                domain.append(('patient_id', '=', rec.patient_id.id))
            
            # Date filter: appointments from last 30 days to future
            cutoff_date = fields.Date.today() - datetime.timedelta(days=30)
            domain.append(('appointment_date', '>=', cutoff_date))
            
            appointments = self.env['dental.appointment'].search(domain)
            rec.appointment_ids = appointments.ids
            
            _logger.info(f"Prescription {rec.id}: Patient={rec.patient_id.name if rec.patient_id else 'None'}, "
                        f"Domain={domain}, Found={len(appointments)} appointments: {appointments.mapped('appointment_no')}")

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """When patient changes, clear appointment_id and recompute available appointments."""
        if self.patient_id:
            self.appointment_id = False
            # Force recomputation of appointment_ids
            self._compute_appointment_ids()
            
            # Create dynamic domain for appointment selection
            domain = [
                ('patient_id', '=', self.patient_id.id),
                ('state', '!=', 'cancelled'),
                ('appointment_date', '>=', (fields.Date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'))
            ]
            
            return {
                'domain': {
                    'appointment_id': domain
                }
            }
        else:
            self.appointment_id = False
            self.appointment_ids = []
            return {
                'domain': {
                    'appointment_id': [('id', 'in', [])]
                }
            }

    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        """When appointment is selected, update related fields"""
        if self.appointment_id:
            # Force update of related fields
            self.patient_id = self.appointment_id.patient_id
            self.prescribed_doctor_id = self.appointment_id.dentist_id
            
            _logger.info(f"Appointment selected: {self.appointment_id.appointment_no}, "
                        f"Patient: {self.patient_id.name if self.patient_id else 'None'}, "
                        f"Doctor: {self.prescribed_doctor_id.name if self.prescribed_doctor_id else 'None'}")
        else:
            # Clear related fields when no appointment is selected
            self.patient_id = False
            self.prescribed_doctor_id = False

    def action_prescribed(self):
        """Marks the prescription and its associated appointment as `done`.
        This method updates the state of both the DentalPrescription instance
        and its linked dental.appointment instance to `done`, indicating that
        the prescription has been finalized and the appointment has been completed.
        """
        self.state = 'done'
        self.appointment_id.state = 'done'

    def create_invoice(self):
        """Create two separate invoices: one for treatment and one for prescribed medicines."""
        self.ensure_one()

        if not self.treatment_id:
            raise UserError(_("No treatment selected."))

        # ---------- TREATMENT INVOICE ----------
        treatment_invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.patient_id.id,
            'state': 'draft',
            'invoice_line_ids': [
                fields.Command.create({
                    'name': self.treatment_id.name,
                    'quantity': 1,
                    'price_unit': self.cost,
                })
            ],
            'is_treatment_invoice': True,
        }
        treatment_invoice = self.env['account.move'].create(treatment_invoice_vals)

        # ---------- PRESCRIPTION INVOICE ----------
        medicine_invoice_lines = []
        medicine_moves = []
        for rec in self.medicine_ids:
            product = self.env['product.product'].search([
                ('product_tmpl_id', '=', rec.medicament_id.id)], limit=1)
            if product:
                # Add medicine line
                medicine_invoice_lines.append(
                    fields.Command.create({
                        'product_id': product.id,
                        'name': rec.display_name,
                        'quantity': rec.quantity,
                        'price_unit': rec.price,
                    })
                )

                # Track movement if stockable
                if product.type == 'consu':
                    medicine_moves.append({
                        'product_id': product,
                        'quantity': rec.quantity,
                    })

        if not medicine_invoice_lines:
            raise UserError(_("No valid medicines to invoice."))

        prescription_invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.patient_id.id,
            'state': 'draft',
            'invoice_line_ids': medicine_invoice_lines,
        }
        prescription_invoice = self.env['account.move'].create(prescription_invoice_vals)

        # ---------- STOCK MOVEMENT ----------
        if medicine_moves:
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
            if not warehouse:
                raise UserError(_('No warehouse found for the company. Please configure a warehouse.'))

            source_location = warehouse.lot_stock_id
            customer_location = self.env.ref('stock.stock_location_customers')

            for move in medicine_moves:
                self.env['stock.move'].create({
                    'name': f'Prescription {self.sequence_no}',
                    'product_id': move['product_id'].id,
                    'product_uom_qty': move['quantity'],
                    'quantity': move['quantity'],
                    'product_uom': move['product_id'].uom_id.id,
                    'location_id': source_location.id,
                    'location_dest_id': customer_location.id,
                    'state': 'done',
                })

        # Link only treatment invoice (or both if needed)
        self.invoice_data_id = treatment_invoice.id
        self.state = 'invoiced'

        # ---------- RETURN BOTH INVOICES ----------
        return {
            'type': 'ir.actions.act_window',
            'name': 'Treatment & Prescription Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', [treatment_invoice.id, prescription_invoice.id])],
            'context': "{'move_type':'out_invoice'}",
        }

    def action_view_invoice(self):
        """Invoice view"""
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_data_id.id,
        }
    def action_print_prescription(self):
        return self.env.ref('dental_hospital.report_pdf_dental_prescription').report_action(self)

    def action_open_patient_payments(self):
        self.ensure_one()
        return self.patient_id.with_context({
            'default_treatment_name': self.treatment_id.name,
            'default_treatment_cost': self.cost
        }).action_open_patient_payments()




class DentalPrescriptionLines(models.Model):
    """Prescription lines of the dental clinic prescription"""
    _name = 'dental.prescription_lines'
    _description = "Dental Prescriptions Lines"
    _rec_name = "medicament_id"

    medicament_id = fields.Many2one('product.template',
                                    domain="[('is_medicine', '=', True)]",
                                    string="Medicament",
                                    help="Name of the medicine")
    generic_name = fields.Char(string="Generic Name",
                               related="medicament_id.generic_name",
                               help="Generic name of the medicament")
    dosage_strength = fields.Integer(string="Dosage Strength",
                                     related="medicament_id.dosage_strength",
                                     help="Dosage strength of medicament")
    medicament_form = fields.Selection([('tablet', 'Tablets'),
                             ('capsule', 'Capsules'),
                             ('liquid', 'Liquid'),
                             ('injection', 'Injections')],
                            string="Medicament Form",
                            required=True,
                            help="Add the form of the medicine")
    quantity = fields.Integer(string="Quantity",
                              required=True,
                              help="Quantity of medicine")
    # frequency_id = fields.Many2one('medicine.frequency',
    #                                string="Frequency",
    #                                required=True,
    #                                help="Frequency of medicine")
    price = fields.Float(related='medicament_id.list_price',
                          string="Price",
                          help="Cost of medicine")
    prescription_id = fields.Many2one('dental.prescription',
                                      help="Relate the model with dental_prescription")
    morning = fields.Boolean(string="Morning")
    noon = fields.Boolean(string="After Noon")
    night = fields.Boolean(string="Night")
    medicine_take = fields.Selection([
        ('before', 'Before Food'),
        ('after', 'After Food')
    ], string='Medicine Take',default='after')
    days = fields.Float(string='Days')




