import "dotenv/config";
import axios from "axios";
import FormData from "form-data";
import watch from "node-watch";
import amqp from "amqplib";

const { NEXTCLOUD_WEBDAV = "http://nextcloud/remote.php/dav/files/admin",
        NEXTCLOUD_USER = "admin",
        NEXTCLOUD_PASSWORD = "admin123",
        OPENMRS_URL = "http://openmrs:8080/openmrs",
        RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672" } = process.env;

const localDir = "/app/new-results";    // monta un volumen si lo deseas
let channel;

async function connectRabbit() {
  const conn = await amqp.connect(RABBITMQ_URL);
  channel = await conn.createChannel();
  await channel.assertExchange("clinic", "topic", { durable: true });
  console.log("Lab-uploader conectado a RabbitMQ");
}

async function uploadFile(filePath) {
  const fileName = filePath.split("/").pop();
  const stream = (await import("fs")).createReadStream(filePath);
  const form = new FormData();
  form.append("file", stream, fileName);

  await axios.put(`${NEXTCLOUD_WEBDAV}/${fileName}`, stream, {
    auth: { username: NEXTCLOUD_USER, password: NEXTCLOUD_PASSWORD },
    headers: { "Content-Type": "application/pdf" }
  });

  await channel.publish(
    "clinic",
    "lab.new-result",
    Buffer.from(JSON.stringify({ file: fileName }))
  );
  console.log("Subido y notificado:", fileName);
}

(async () => {
  await connectRabbit();
  watch(localDir, { recursive: false }, (_, file) => uploadFile(file));
})();
