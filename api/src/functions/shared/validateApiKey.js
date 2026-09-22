/**
 * Validates the X-App-Key header against the APP_API_KEY environment variable.
 * NOTE: the key is shipped to the browser, so it is NOT a real secret — it only
 * deters casual non-app callers. Real protection is per-user login + CORS.
 *
 * Uses its own STOTT_APP_API_KEY so Stott and Classroom-survivors keys stay
 * independent: rotating one never affects the other.
 */
const OWN_ORIGINS = [
    /vpietri-stack\.github\.io$/i,
    /azurestaticapps\.net$/i,
];

function originOf(request) {
    return request.headers.get('origin') || request.headers.get('referer') || '';
}

function isLocalhost(request) {
    // Only inspect Origin/Referer: in the Azure Functions host request.url is
    // always the INTERNAL http://localhost:<port> URL, so using it would
    // wrongly whitelist every production request as "localhost".
    const o = originOf(request);
    return /^(https?:\/\/localhost|https?:\/\/127\.0\.0\.1)/i.test(o);
}

function isOwnOrigin(request) {
    return OWN_ORIGINS.some(re => re.test(originOf(request)));
}

function validateApiKey(request) {
    const expectedKey = process.env.APP_API_KEY;
    const sentKey = request.headers.get('X-App-Key') || '';

    if (expectedKey && sentKey === expectedKey) return true;
    if (isOwnOrigin(request)) return true;
    if (isLocalhost(request) && !sentKey) return true;
    if (!expectedKey) return true;

    return false;
}

module.exports = { validateApiKey };
