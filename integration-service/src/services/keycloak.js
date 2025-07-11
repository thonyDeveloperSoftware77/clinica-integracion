import axios from 'axios';

const KEYCLOAK_URL = process.env.KEYCLOAK_URL || 'http://keycloak:8080';

export async function getKeycloakToken() {
  const response = await axios.post(`${KEYCLOAK_URL}/auth/realms/clinica/protocol/openid-connect/token`, {
    client_id: 'clinica-client',
    client_secret: 'client_secret',
    grant_type: 'client_credentials'
  });
  return response.data.access_token;
}