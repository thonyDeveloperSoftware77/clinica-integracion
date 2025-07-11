import Fastify from 'fastify';
import cors from '@fastify/cors';
import appointmentsRoutes from './routes/appointments.js';
import logger from './services/logger.js';

const fastify = Fastify({ logger: false });

// Configuración de Fastify
await fastify.register(cors);
await fastify.register(appointmentsRoutes, { prefix: '/v1' });

// Iniciar servidor
try {
  await fastify.listen({ port: process.env.PORT || 3001, host: '0.0.0.0' });
  logger.info(`Servicio de integración iniciado en puerto ${process.env.PORT || 3001}`);
} catch (err) {
  logger.error(`Error iniciando el servidor: ${err.message}`);
  process.exit(1);
}