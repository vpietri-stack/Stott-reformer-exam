const { app } = require('@azure/functions');
const { validateApiKey } = require('./shared/validateApiKey');
const { getContainer } = require('./shared/db');
const auth = require('./shared/auth');

// Logout: clears the account's activeSid so the current token stops working.
// Even without calling this, a newer login elsewhere kicks this device out.
app.http('logout', {
    route: 'logout',
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        try {
            if (!validateApiKey(request)) return { status: 403, body: 'Forbidden.' };

            const token = auth.verifyToken(request, auth.SESSION_SECRET());
            if (!token || !token.sid) return { status: 200, jsonBody: { ok: true } };

            try {
                const { resource: user } = await getContainer().item(token.sub, token.login || token.sub).read();
                if (user && user.activeSid === token.sid) {
                    user.activeSid = null;
                    await getContainer().items.upsert(user);
                }
            } catch (err) {
                if (!err || err.code !== 404) throw err;
            }
            return { status: 200, jsonBody: { ok: true } };
        } catch (error) {
            context.error('Logout error:', error);
            return { status: 200, jsonBody: { ok: true } };
        }
    }
});
