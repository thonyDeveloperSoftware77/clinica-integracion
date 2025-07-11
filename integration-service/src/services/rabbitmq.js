import amqp from 'amqplib';

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://guest:guest@rabbitmq:5672';

export async function publishMessage(message) {
  const conn = await amqp.connect(RABBITMQ_URL);
  const channel = await conn.createChannel();
  await channel.assertQueue('notifications');
  channel.sendToQueue('notifications', Buffer.from(JSON.stringify(message)));
  await channel.close();
  await conn.close();
}