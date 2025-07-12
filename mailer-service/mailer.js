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
              <h2 style="color: #27ae60;">✅ Ticket Creado Exitosamente</h2>
              
              <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0; color: #155724; font-weight: bold;">
                  ¡Hola ${data.user_name}! Tu reporte de incidente ha sido creado exitosamente en el sistema.
                </p>
              </div>
              
              <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #34495e; margin-top: 0;">📋 Detalles del Ticket</h3>
                <table style="width: 100%; border-collapse: collapse;">
                  <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Número de Referencia:</td>
                    <td style="padding: 8px 0;">${data.name}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Prioridad:</td>
                    <td style="padding: 8px 0;">
                      <span style="background-color: ${priorityColor}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">
                        ${priorityText}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Estado:</td>
                    <td style="padding: 8px 0;">
                      <span style="background-color: ${getStatusColor(data.state)}; color: white; padding: 4px 8px; border-radius: 4px;">
                        ${getStatusText(data.state)}
                      </span>
                    </td>
                  </tr>
                </table>
              </div>
              
              <div style="background-color: #fff; border-left: 4px solid ${priorityColor}; padding: 15px; margin: 20px 0;">
                <h4 style="margin-top: 0; color: #2c3e50;">📝 Tu Descripción del Incidente:</h4>
                <p style="line-height: 1.6; color: #555; margin-bottom: 0;">${data.description.replace(/\n/g, '<br>')}</p>
              </div>
              
              <div style="margin-top: 30px; padding: 15px; background-color: #e8f5e8; border-radius: 6px; text-align: center;">
                <p style="margin: 0; color: #2d5a2d; font-size: 14px;">
                  🎯 Tu ticket ha sido enviado al sistema Zammad y será procesado por nuestro equipo de soporte.
                  ${data.priority === 'critico' ? '<br><strong>⚠️ Debido a la prioridad CRÍTICA, se ha notificado al administrador del sistema.</strong>' : ''}
                  Recibirás actualizaciones sobre el progreso de tu reporte.
                </p>
              </div>
            </div>
          `
        }, {
          headers: {
            Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
            'Content-Type': 'application/json'
          }
        });

        console.log(`✅ Correo de confirmación enviado correctamente a: ${recipients.join(', ')}`);
        if (data.priority === 'critico') {
          console.log(`🚨 ALERTA CRÍTICA: Se ha notificado al administrador sobre el incidente ${data.name}`);
        }
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
