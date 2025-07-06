import axios from "axios";
const url = "http://localhost:8069/jsonrpc";
const payload = {
  jsonrpc: "2.0",
  method: "object",
  params: {
    service: "res.partner",
    method: "create",
    args: [{
      name: "Juan Pérez",
      email: "juan@example.com",
      phone: "0999999999"
    }]
  },
  id: 1
};
await axios.post(url, payload);
console.log("Partner demo creado");
