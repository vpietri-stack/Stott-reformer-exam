// Serve the app over http://localhost:8123 for manual/browser testing (no dependencies).
//   node tools/serve-local.mjs
// The login gate blocks the exam UI, and the auth API is not running locally, so in the
// browser console use:
//   localStorage.setItem('stottSessionToken','test'); stottShowApp(); startGame();
import http from 'http';
import fs from 'fs';
import path from 'path';

const root = process.cwd();
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json' };

http.createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split('?')[0]);
  const file = path.join(root, rel === '/' ? 'index.html' : rel);
  if (!file.startsWith(root)) { res.writeHead(403).end('403'); return; }
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404).end('404'); return; }
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
    res.end(buf);
  });
}).listen(8123, () => console.log('serving ' + root + ' on http://localhost:8123'));
