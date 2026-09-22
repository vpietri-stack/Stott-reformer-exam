// Admin tool for Stott exam accounts. Run from the api/ folder:
//   node scripts/stott_admin.js create <login> "<full name>" <password>
//   node scripts/stott_admin.js reset <login> <new-password>
//   node scripts/stott_admin.js disable <login>
//   node scripts/stott_admin.js enable <login>
//   node scripts/stott_admin.js list
//
// Needs COSMOS_ENDPOINT + COSMOS_KEY in env (or api/local.settings.json
// Values). Passwords are stored as scrypt hashes only — they cannot be
// looked up later. A forgotten password = `reset` issues a new one.
const { CosmosClient } = require('@azure/cosmos');
const crypto = require('crypto');

function loadLocalSettings() {
    try {
        const s = require('../local.settings.json');
        for (const [k, v] of Object.entries(s.Values || {})) {
            if (!process.env[k]) process.env[k] = v;
        }
    } catch {}
}

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(String(password), salt, 32).toString('hex');
    return `scrypt$${salt}$${hash}`;
}

async function main() {
    loadLocalSettings();
    const [cmd, a, b, c] = process.argv.slice(2);
    const client = new CosmosClient({
        endpoint: process.env.COSMOS_ENDPOINT,
        key: process.env.COSMOS_KEY,
    });
    const container = client
        .database(process.env.COSMOS_DB_NAME || 'Val-EslApp')
        .container(process.env.COSMOS_CONTAINER_NAME || 'StottUsers');

    if (cmd === 'list') {
        const { resources } = await container.items
            .query('SELECT c.id, c.login, c.fullName, c.disabled, c.lastLoginAt FROM c')
            .fetchAll();
        for (const u of resources) {
            console.log(`${u.disabled ? '[disabled]' : '[active]'} ${u.login} — ${u.fullName || ''} (last login: ${u.lastLoginAt || 'never'})`);
        }
        return;
    }

    if (cmd === 'create') {
        const login = String(a || '').trim().toLowerCase();
        const fullName = b || '';
        const password = c || '';
        if (!login || !password) {
            console.error('Usage: create <login> "<full name>" <password>');
            process.exit(1);
        }
        if (password.length < 6) {
            console.error('Password must be at least 6 characters.');
            process.exit(1);
        }
        const doc = {
            id: login,
            login,
            fullName,
            password: hashPassword(password),
            activeSid: null,
            disabled: false,
            createdAt: new Date().toISOString(),
        };
        await container.items.create(doc);
        console.log(`Created account "${login}" (${fullName}).`);
        return;
    }

    if (cmd === 'reset') {
        const login = String(a || '').trim().toLowerCase();
        const password = b || '';
        if (!login || !password || password.length < 6) {
            console.error('Usage: reset <login> <new-password> (min 6 chars)');
            process.exit(1);
        }
        const { resource: user } = await container.item(login, login).read();
        if (!user) {
            console.error(`No such account: ${login}`);
            process.exit(1);
        }
        user.password = hashPassword(password);
        user.activeSid = null; // kick all devices; user logs in fresh
        await container.items.upsert(user);
        console.log(`Password reset for "${login}". All devices logged out.`);
        return;
    }

    if (cmd === 'disable' || cmd === 'enable') {
        const login = String(a || '').trim().toLowerCase();
        if (!login) {
            console.error(`Usage: ${cmd} <login>`);
            process.exit(1);
        }
        const { resource: user } = await container.item(login, login).read();
        if (!user) {
            console.error(`No such account: ${login}`);
            process.exit(1);
        }
        user.disabled = cmd === 'disable';
        user.activeSid = null;
        await container.items.upsert(user);
        console.log(`Account "${login}" ${cmd}d.`);
        return;
    }

    console.error('Commands: list | create | reset | disable | enable');
    process.exit(1);
}

main().catch((e) => {
    if (e && e.code === 409) console.error('That login already exists.');
    else console.error('Error:', e.message || e);
    process.exit(1);
});
