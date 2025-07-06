import "dotenv/config";
import axios from "axios";
import amqp from "amqplib";
import cron from "node-cron";

const { OPENMRS_URL = "http://openmrs:8080/openmrs",
        ODOO_URL   = "http://odoo:8069/jsonrpc",
        RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672" } = process.env;

let channel;

async function connectRabbit() {
  const conn = await amqp.connect(RABBITMQ_URL);
  channel = await conn.createChannel();
  await channel.assertExchange("clinic", "topic", { durable: true });
  console.log("Bridge-billing conectado a RabbitMQ");
}

async function syncLastEncounter() {
  const { data } = await axios.get(
    `${OPENMRS_URL}/ws/rest/v1/encounter?limit=1`,
    { auth: { username: "doctor", password: "doctor123" } }
  );
  const enc = data?.results?.[0];
  if (!enc) return;

  const payload = {
    jsonrpc: "2.0",
    method: "object",
    params: {
      service: "account.move",
      method: "create",
      args: [{
        move_type: "out_invoice",
        partner_id: 3,
        invoice_line_ids: [[0, 0, {
          name: `Consulta ${enc.uuid}`,
          quantity: 1,
          price_unit: 25.0
        }]]
      }]
    },
    id: Math.random()
  };
  await axios.post(ODOO_URL, payload);

  await channel.publish(
    "clinic",
    "billing.synced",
    Buffer.from(JSON.stringify({ encounter: enc.uuid }))
  );
  console.log("Factura generada para encounter:", enc.uuid);
}

(async () => {
  await connectRabbit();
  // Cada 2 minutos
  cron.schedule("*/2 * * * *", syncLastEncounter);
})();
