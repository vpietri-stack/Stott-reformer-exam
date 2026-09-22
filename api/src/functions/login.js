const { app } = require('@azure/functions');
const { validateApiKey } = require('./shared/validateApiKey');
const { getContainer } = require('./shared/db');
const auth = require('./shared/auth');

app.http('login', {
    route: 'login',
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        try {
            if (!validateApiKey(request)) return { status: 403, body: 'Forbidden.' };

            const secret = auth.SESSION_SECRET();
            if (!secret) {
                context.error('SESSION_SECRET is not configured.');
                return { status: 500, body: 'Server misconfigured.' };
            }

            const body = await request.json();
            const login = String(body.login || '').trim().toLowerCase();
            const password = body.password;
            if (!login || !password) return { status: 401, body: 'Invalid credentials.' };

            // Partition key is /login and docs use id === login, so a point
            // read is enough (no cross-partition query needed).
            let user = null;
            try {
                const { resource } = await getContainer().item(login, login).read();
                user = resource || null;
            } catch (err) {
                if (err && err.code !== 404) throw err;
            }
            if (!user || user.disabled) return { status: 401, body: 'Invalid credentials.' };
            if (!auth.verifyPassword(password, user.password)) {
                return { status: 401, body: 'Invalid credentials.' };
            }

            // Single-session: mint a fresh sid and stamp it. Any older token
            // carrying a different sid is rejected by /api/session, so two
            // devices cannot share one account at the same time.
            const sid = auth.newSessionId();
            user.activeSid = sid;
            user.lastLoginAt = new Date().toISOString();
            await getContainer().items.upsert(user);

            const token = auth.signToken(
                { sub: user.id, login: user.login, sid, name: user.fullName },
                secret
            );
            return { status: 200, jsonBody: { ...auth.publicUser(user), token } };
        } catch (error) {
            context.error('Login error:', error);
            return { status: 500, body: 'Server error during login.' };
        }
    }
});
