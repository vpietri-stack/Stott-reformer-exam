const crypto = require('crypto');

// ============================================================================
// Session-token auth helper for the Stott exam app.
//
// Same JWT-shaped HMAC-SHA256 design as Classroom-survivors, but standalone:
//  - Passwords are scrypt hashes ONLY. There is no plaintext storage and no
//    legacy-plaintext fallback. A forgotten password = admin issues a new one.
//  - Single-session enforcement: login mints a random `sid`, stores it as the
//    user's `activeSid`, and embeds it in the token. The session endpoint
//    rejects any token whose sid no longer matches — so a second login on
//    another device kicks the first one out.
//  - The client token travels in `X-Auth-Token` (Azure SWA's proxy overwrites
//    the `Authorization` header with its own internal token).
// ============================================================================

const DEFAULT_TTL = 30 * 24 * 3600; // 30 days (seconds)

function b64url(buf) {
    return Buffer.from(buf)
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
}

function b64urlJson(obj) {
    return b64url(JSON.stringify(obj));
}

function fromB64url(str) {
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    while (str.length % 4) str += '=';
    return Buffer.from(str, 'base64');
}

function signToken(payload, secret, ttlSeconds = DEFAULT_TTL) {
    const header = { alg: 'HS256', typ: 'JWT' };
    const now = Math.floor(Date.now() / 1000);
    const body = { ...payload, iat: now, exp: now + ttlSeconds };
    const data = `${b64urlJson(header)}.${b64urlJson(body)}`;
    const sig = crypto.createHmac('sha256', secret).update(data).digest();
    return `${data}.${b64url(sig)}`;
}

function verifyTokenString(token, secret) {
    if (!token || !secret) return null;
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const [h, p, s] = parts;
    const expected = b64url(
        crypto.createHmac('sha256', secret).update(`${h}.${p}`).digest()
    );
    const a = Buffer.from(expected);
    const b = Buffer.from(s);
    if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
    let payload;
    try {
        payload = JSON.parse(fromB64url(p).toString('utf8'));
    } catch {
        return null;
    }
    if (!payload.exp || payload.exp < Math.floor(Date.now() / 1000)) return null;
    return payload; // { sub, login, sid, name, iat, exp }
}

function getBearer(request) {
    const headers = request.headers || {};
    const get = (name) =>
        headers.get ? headers.get(name) : headers[name] || '';
    const xAuth = get('X-Auth-Token');
    if (xAuth) return xAuth;
    const auth = get('Authorization');
    if (auth) {
        const m = auth.match(/^Bearer\s+(.+)$/i);
        if (m) return m[1];
    }
    return null;
}

function verifyToken(request, secret) {
    return verifyTokenString(getBearer(request), secret);
}

const SESSION_SECRET = () => process.env.SESSION_SECRET || '';

function newSessionId() {
    return crypto.randomBytes(16).toString('hex');
}

// ---------------------------------------------------------------------------
// Password hashing (scrypt, per-user salt). Hashes ONLY — a forgotten password
// cannot be looked up; the admin issues a new one (scripts/stott_admin.js).
// ---------------------------------------------------------------------------
function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(String(password), salt, 32).toString('hex');
    return `scrypt$${salt}$${hash}`;
}

function verifyPassword(password, stored) {
    if (!password || !stored || !stored.startsWith('scrypt$')) return false;
    const [, salt, hash] = stored.split('$');
    if (!salt || !hash) return false;
    const calc = crypto.scryptSync(String(password), salt, 32).toString('hex');
    const a = Buffer.from(hash);
    const b = Buffer.from(calc);
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Remove credential/PII fields before returning a user object to the client.
// Also drops Cosmos metadata (_rid/_self/_etag/_attachments/_ts).
function publicUser(user) {
    if (!user) return user;
    const { password, activeSid, _rid, _self, _etag, _attachments, _ts, ...rest } = user;
    return rest;
}

module.exports = {
    signToken,
    verifyToken,
    verifyTokenString,
    getBearer,
    SESSION_SECRET,
    newSessionId,
    hashPassword,
    verifyPassword,
    publicUser,
    DEFAULT_TTL,
};
