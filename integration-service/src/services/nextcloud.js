import { createClient } from 'webdav';

const NEXTCLOUD_URL = process.env.NEXTCLOUD_URL || 'http://nextcloud:80';
const webdavClient = createClient(`${NEXTCLOUD_URL}/remote.php/dav/files/admin/`, {
  username: 'admin',
  password: 'admin_password'
});

export async function uploadToNextcloud(content, filename) {
  await webdavClient.putFileContents(`/reports/${filename}`, Buffer.from(content));
}