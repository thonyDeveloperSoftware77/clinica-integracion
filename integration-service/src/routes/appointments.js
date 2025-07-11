import axios from 'axios';
import { createClient } from 'webdav';
import { publishMessage } from '../services/rabbitmq.js';
import { createOdooAppointment } from '../services/odoo.js';
import { createZammadTicket } from '../services/zammad.js';
import { uploadToNextcloud } from '../services/nextcloud.js';
import { getKeycloakToken } from '../services/keycloak.js';
import logger from '../services/logger.js';

export default async function routes(fastify, options) {
  fastify.post('/appointments', async (request, reply) => {
    const { patient_id, doctor_id, date, description } = request.body;

    // Validación básica
    if (!patient_id || !doctor_id || !date) {
      logger.error('Solicitud inválida: faltan campos requeridos');
      return reply.status(400).send({ error: 'Solicitud inválida' });
    }

    try {
      // Autenticación con Keycloak
      const token = await getKeycloakToken();
      logger.info('Autenticación exitosa con Keycloak');

      // Crear cita en Odoo
      const appointment_id = await createOdooAppointment(token, { patient_id, doctor_id, date, description });
      logger.info(`Cita creada en Odoo: ID ${appointment_id}`);

      // Sincronizar con Zammad
      const zammad_ticket_id = await createZammadTicket(token, patient_id, date, description);
      logger.info(`Ticket creado en Zammad: ID ${zammad_ticket_id}`);

      // Subir informe a Nextcloud
      await uploadToNextcloud(`Informe de cita: ${description}`, `cita_${appointment_id}.pdf`);
      logger.info(`Informe subido a Nextcloud: cita_${appointment_id}.pdf`);

      // Publicar notificación en RabbitMQ
      await publishMessage({
        appointment_id,
        message: `Cita creada: ${patient_id} para ${date}`
      });
      logger.info('Notificación publicada en RabbitMQ');

      // Respuesta exitosa
      return reply.status(201).send({
        appointment_id,
        status: 'created',
        zammad_ticket_id
      });
    } catch (error) {
      logger.error(`Error en la integración: ${error.message}`);
      return reply.status(500).send({ error: 'Error en la integración' });
    }
  });
}