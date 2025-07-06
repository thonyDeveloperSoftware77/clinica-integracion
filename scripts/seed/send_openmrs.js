import axios from "axios";
const base = "http://localhost:8080/openmrs/ws/rest/v1";
const auth = { username: "doctor", password: "doctor123" };

await axios.post(`${base}/patient`, {
  person: {
    names: [{ givenName: "Juan", familyName: "Pérez" }],
    gender: "M",
    birthdate: "1990-01-01"
  },
  identifiers: [{
    identifier: "0001",
    identifierType: "05a29f94-c0ed-11e2-94be-8c13b969e334",
    location: "8d6c993e-c2cc-11de-8d13-0010c6dffd0f",
    preferred: true
  }]
}, { auth });
console.log("Paciente demo creado");
