import winston from 'winston';
import 'winston-loki';

const LOKI_URL = process.env.LOKI_URL || 'http://loki:3100';

const logger = winston.createLogger({
  transports: [
    new winston.transports.Loki({
      host: LOKI_URL,
      labels: { app: 'integration-service' }
    }),
    new winston.transports.Console()
  ]
});

export default logger;