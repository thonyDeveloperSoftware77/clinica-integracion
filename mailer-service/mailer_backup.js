// mailer.js
import amqp from 'amqplib';
import axios from 'axios';
import 'dotenv/config';

const ZAMMAD_QUEUE = 'zammad_alerts';

async function main() {
  const conn = await amqp.connect('amqp://guest:guest@rabbitmq:5672');
  const channel = await conn.createChannel();
  
  // Assert queue
  await channel.assertQueue(ZAMMAD_QUEUE, { durable: false });

  console.log(`🟢 Escuchando mensajes en la cola "${ZAMMAD_QUEUE}"...`);

  // Listen for Zammad alerts
  channel.consume(ZAMMAD_QUEUE, async (msg) => {
    if (msg !== null) {
      const data = JSON.parse(msg.content.toString());
      console.log("📨 Mensaje de incidente recibido:", data);

      try {
        // Determinar destinatarios según la prioridad
        let recipients = [data.user_email]; // Siempre enviar al usuario que creó el incidente
        let subjectPrefix = '';
        let priorityColor = '#3498db';
        let priorityText = 'Normal';
        
        // Si es crítico, también enviar al admin
        if (data.priority === 'critico') {
          recipients.push('admin22@admin.com');
          subjectPrefix = '[CRÍTICO] ';
          priorityColor = '#e74c3c';
          priorityText = 'Crítico';
        } else if (data.priority === 'alto') {
          subjectPrefix = '[ALTO] ';
          priorityColor = '#f39c12';
          priorityText = 'Alto';
        } else {
          priorityColor = '#27ae60';
          priorityText = 'Normal';
        }

        await axios.post('https://api.resend.com/emails', {
          from: 'Zeppelin Reports <reports@message.focused.uno>',
          to: recipients,
          subject: `${subjectPrefix}✅ Ticket Creado Exitosamente - ${data.name}`,
          html: `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
              <h2 style="color: #2c3e50;">� Nuevo Incidente Reportado</h2>
              
              <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #34495e; margin-top: 0;">Detalles del Incidente</h3>
                <table style="width: 100%; border-collapse: collapse;">
                  <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Referencia:</td>
                    <td style="padding: 8px 0;">${data.name}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Estado:</td>
                    <td style="padding: 8px 0;">
                      <span style="background-color: ${getStatusColor(data.state)}; color: white; padding: 4px 8px; border-radius: 4px;">
                        ${getStatusText(data.state)}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Reportado por:</td>
                    <td style="padding: 8px 0;">${data.user_name}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Email:</td>
                    <td style="padding: 8px 0;">${data.user_email}</td>
                  </tr>
                </table>
              </div>
              
              <div style="background-color: #fff; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0;">
                <h4 style="margin-top: 0; color: #2c3e50;">📝 Descripción del Incidente:</h4>
                <p style="line-height: 1.6; color: #555; margin-bottom: 0;">${data.description.replace(/\n/g, '<br>')}</p>
              </div>
            </div>
          `
        }, {
          headers: {
            Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
            'Content-Type': 'application/json'
          }
        });

        console.log("✅ Correo de confirmación enviado correctamente.");
        channel.ack(msg);
      } catch (err) {
        console.error("❌ Error al enviar correo:", err.message);
        console.error("Detalles del error:", err.response?.data || err);
      }
    }
  });
}

// Helper functions for email formatting
function getStatusColor(state) {
  const colors = {
    'draft': '#95a5a6',
    'sent': '#3498db', 
    'in_progress': '#f39c12',
    'closed': '#27ae60'
  };
  return colors[state] || '#95a5a6';
}

function getStatusText(state) {
  const texts = {
    'draft': 'Borrador',
    'sent': 'Enviado a Zammad',
    'in_progress': 'En Progreso', 
    'closed': 'Cerrado'
  };
  return texts[state] || state;
}

main().catch(console.error);
