import axios from 'axios';

const ODOO_URL = process.env.ODOO_URL || 'http://odoo:8069';

export async function createOdooAppointment(token, { patient_id, doctor_id, date, description }) {
  const response = await axios.post(`${ODOO_URL}/jsonrpc`, {
    jsonrpc: '2.0',
    method: 'call',
    params: {
      service: 'object',
      method: 'execute_kw',
      args: [
        'clinica_db',
        1,
        'admin_password',
        'calendar.event',
        'create',
        [{
          partner_id: patient_id,
          user_id: doctor_id,
          start: date,
          description: description
        }]
      ]
    }
  }, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data.result;
}