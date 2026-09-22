const { app } = require('@azure/functions');
const { validateApiKey } = require('./shared/validateApiKey');
const { getContainer } = require('./shared/db');
const auth = require('./shared/auth');

// Heartbeat: the client calls this every few minutes. It verifies the token
// AND that its sid still matches the account's current activeSid. A second
// login elsewhere overwrites activeSid, so the older device gets
// { kicked: true } and is sent back to the login screen.
app.http('session', {
    route: 'session',
    methods: ['GET'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        try {
            if (!validateApiKey(request)) return { status: 403, body: 'Forbidden.' };

            const token = auth.verifyToken(request, auth.SESSION_SECRET());
            if (!token || !token.sid) return { status: 401, body: 'Unauthorized.' };

            let user = null;
            try {
                const { resource } = await getContainer().item(token.sub, token.login || token.sub).read();
                user = resource || null;
            } catch (err) {
                if (err && err.code !== 404) throw err;
            }
            if (!user || user.disabled) return { status: 401, body: 'Unauthorized.' };

            if (user.activeSid !== token.sid) {
                return { status: 200, jsonBody: { kicked: true } };
            }
            return { status: 200, jsonBody: { ok: true, ...auth.publicUser(user) } };
        } catch (error) {
            context.error('Session error:', error);
            return { status: 500, body: 'Server error.' };
        }
    }
});
