import axios from 'axios';

const ZAMMAD_URL = process.env.ZAMMAD_URL || 'http://zammad:8080';

export async function createZammadTicket(token, patient_id, date, description) {
  const response = await axios.post(`${ZAMMAD_URL}/api/v1/tickets`, {
    title: `Cita para paciente ${patient_id}`,
    group: 'Soporte',
    customer_id: patient_id,
    article: {
      subject: 'Nueva cita',
      body: `Cita creada para ${date}: ${description}`,
      type: 'note',
      internal: false
    }
  }, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data.id;
}