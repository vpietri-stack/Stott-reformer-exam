// Behaviour tests for the client auth heartbeat (stott_auth.js).
// Plain Node, no framework: node tests/stott_auth_test.js
// The page script is loaded into a stubbed browser environment so its
// timer / visibility / logout behaviour can be observed directly.

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const SRC = fs.readFileSync(process.env.STOTT_AUTH_SRC
    || path.join(__dirname, '..', 'stott_auth.js'), 'utf8');
const flush = () => new Promise(r => setImmediate(r));
async function drain(rounds = 6) {
    for (let i = 0; i < rounds; i++) await flush();
}

function makeEnv() {
    const listeners = {};
    const timers = [];
    const calls = [];
    const queue = [];
    const store = new Map();
    const els = {};
    let nextId = 1;

    const el = id => (els[id] ||= {
        id,
        classes: new Set(),
        classList: {
            add: c => els[id].classes.add(c),
            remove: c => els[id].classes.delete(c),
            contains: c => els[id].classes.has(c),
        },
        innerText: '', value: '', disabled: false,
    });

    const sandbox = {
        window: {
            addEventListener: (type, fn) => (listeners[type] ||= []).push(fn),
        },
        localStorage: {
            getItem: k => (store.has(k) ? store.get(k) : null),
            setItem: (k, v) => store.set(k, String(v)),
            removeItem: k => store.delete(k),
        },
        document: {
            hidden: false,
            getElementById: el,
            addEventListener: (type, fn) => (listeners[type] ||= []).push(fn),
        },
        fetch: (url, opts) => {
            calls.push({ url, opts });
            // The per-call app-config probe must not consume the queue below.
            if (/app-config/.test(url)) return Promise.resolve(res(200, { APP_API_KEY: 'k' }));
            if (!queue.length) return Promise.resolve(res(200, { ok: true, login: 'student', fullName: 'A Student' }));
            const next = queue.shift();
            if (next.networkFail) return Promise.reject(new TypeError('Failed to fetch'));
            const r = res(next.status, next.body);
            if (next.badBody) r.json = () => Promise.reject(new SyntaxError('Unexpected token <'));
            return Promise.resolve(r);
        },
        setInterval: (cb, ms) => { timers.push({ cb, ms, id: nextId }); return nextId++; },
        clearInterval: id => { const t = timers.find(t => t.id === id); if (t) t.dead = true; },
        showToast: () => {},
        console,
    };
    sandbox.window.location = { hostname: 'localhost' };
    sandbox.globalThis = sandbox;
    sandbox.__clock = { t: 1700000000000 };
    sandbox.__now = () => sandbox.__clock.t;

    function res(status, body) {
        return { ok: status >= 200 && status < 300, status, json: async () => body };
    }

    vm.createContext(sandbox);
    vm.runInContext(SRC, sandbox, { filename: 'stott_auth.js' });
    // The script only reads the clock through Date.now(), so the resume throttle
    // can be driven by replacing that one function inside the realm.
    vm.runInContext('Date.now = __now;', sandbox);

    const fire = async type => {
        for (const fn of listeners[type] || []) await fn({ preventDefault() {} });
        await drain();
    };

    return {
        sandbox,
        calls,
        queue,
        timers,
        store,
        fire,
        advance: ms => { sandbox.__clock.t += ms; },
        loginVisible: () => !el('login-screen').classes.has('hidden'),
        appVisible: () => !el('start-screen').classes.has('hidden'),
        liveTimers: () => timers.filter(t => !t.dead),
        sessionChecks: () => calls.filter(c => /\/session/.test(c.url)).length,
    };
}

const tests = {
    async 'heartbeat re-checks at least once a minute'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        const beat = e.liveTimers()[0];
        assert.ok(beat, 'a heartbeat timer must be running');
        assert.ok(beat.ms <= 60 * 1000, `heartbeat is ${beat.ms}ms, expected <= 60000ms`);
    },

    async 'becoming visible again re-checks the session immediately'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        const before = e.sessionChecks();
        e.sandbox.document.hidden = true;
        e.advance(5 * 60 * 1000);                      // frozen in a background tab
        await e.fire('visibilitychange');              // going hidden: must not call the API
        e.sandbox.document.hidden = false;
        await e.fire('visibilitychange');              // coming back: must check now
        assert.ok(e.sessionChecks() > before,
            'expected an immediate /session check when the page becomes visible');
    },

    // The reported bug: log in elsewhere, come back to device 1 five minutes
    // later, and it is still letting you play.
    async 'a kicked tab that was backgrounded logs out as soon as it is shown'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        e.queue.push({ status: 200, body: { kicked: true } }); // device 2 took the account
        e.sandbox.document.hidden = true;
        await e.fire('visibilitychange');              // device 1 is put in the background
        e.advance(5 * 60 * 1000);
        e.sandbox.document.hidden = false;
        await e.fire('visibilitychange');              // the user returns to it
        assert.strictEqual(e.queue.length, 0, 'the check must have consumed the kicked reply');
        assert.ok(!e.store.has('stottSessionToken'), 'a kicked session must not survive being backgrounded');
        assert.ok(e.loginVisible(), 'the "logged in elsewhere" message should be on screen');
        assert.strictEqual(e.liveTimers().length, 0, 'the heartbeat must stop once logged out');
    },

    async 'repeated rejected checks log the device out'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        const beat = e.liveTimers()[0];
        for (let i = 0; i < 2; i++) { e.queue.push({ status: 500, body: 'err' }); await beat.cb(); }
        await drain();
        assert.ok(!e.store.has('stottSessionToken'),
            'a session that keeps failing must not stay logged in forever');
        assert.ok(e.loginVisible(), 'login screen should be showing');
    },

    async 'a network drop-out does not log the device out'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        const beat = e.liveTimers()[0];
        for (let i = 0; i < 3; i++) { e.queue.push({ networkFail: true }); await beat.cb(); }
        await drain();
        assert.ok(e.store.has('stottSessionToken'),
            'an offline retry must not be treated as a revoked session');
        assert.ok(!e.loginVisible(), 'login screen should stay hidden while offline');
    },

    async 'an explicit kick logs out on the first check'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        const beat = e.liveTimers()[0];
        e.queue.push({ status: 200, body: { kicked: true } });
        await beat.cb();
        await drain();
        assert.ok(!e.store.has('stottSessionToken'), 'kicked device must drop its token');
        assert.ok(e.loginVisible(), 'kicked device must see the login screen');
    },

    async 'the app-config probe runs once per page load, not per API call'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        const beat = e.liveTimers()[0];
        await beat.cb();
        await beat.cb();
        await drain();
        const configCalls = e.calls.filter(c => /app-config/.test(c.url)).length;
        assert.strictEqual(configCalls, 1, `app-config was fetched ${configCalls} times`);
        assert.ok(e.sessionChecks() >= 3, 'the session checks themselves must still run');
    },

    async 'a rejected token logs out without waiting for a second beat'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        e.queue.push({ status: 401, body: 'Unauthorized.' });
        await e.liveTimers()[0].cb();
        await drain();
        assert.ok(!e.store.has('stottSessionToken'), '401 must end the session immediately');
    },

    async 'an intercepted 200 does not keep the device logged in'() {
        const e = makeEnv();
        e.sandbox.stottSetToken('tok');
        await e.fire('DOMContentLoaded');
        const beat = e.liveTimers()[0];
        for (let i = 0; i < 2; i++) { e.queue.push({ status: 200, badBody: true }); await beat.cb(); }
        await drain();
        assert.ok(!e.store.has('stottSessionToken'), 'an unreadable 200 must end the session too');
    },
};

(async () => {
    let failed = 0;
    for (const [name, run] of Object.entries(tests)) {
        try {
            await run();
            console.log(`  PASS  ${name}`);
        } catch (err) {
            failed++;
            console.log(`  FAIL  ${name}\n        ${err.message}`);
        }
    }
    console.log(failed ? `\n${failed}/${Object.keys(tests).length} failing` : `\nall ${Object.keys(tests).length} passing`);
    process.exit(failed ? 1 : 0);
})();
