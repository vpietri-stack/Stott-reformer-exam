// ============================================================================
// Stott exam client auth — login gate + single-session heartbeat.
// API lives on the Stott-Exam-API Static Web App; this page on GitHub Pages.
// ============================================================================
const STOTT_API_BASE = (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1'
)
    ? 'http://localhost:7075/api'
    : 'https://polite-water-0d9238510.6.azurestaticapps.net/api';

const STOTT_TOKEN_KEY = 'stottSessionToken';
const STOTT_HEARTBEAT_MS = 3 * 60 * 1000; // re-check session every 3 minutes

let stottUser = null;
let stottHeartbeatTimer = null;

function stottGetToken() {
    try { return localStorage.getItem(STOTT_TOKEN_KEY) || null; } catch { return null; }
}
function stottSetToken(token) {
    try {
        if (token) localStorage.setItem(STOTT_TOKEN_KEY, token);
        else localStorage.removeItem(STOTT_TOKEN_KEY);
    } catch {}
}

async function stottApi(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    const token = stottGetToken();
    if (token) headers['X-Auth-Token'] = token;
    // X-App-Key is optional: the API also accepts our GitHub Pages origin.
    try {
        const cfg = await fetch('app-config.json').then(r => (r && r.ok) ? r.json() : null).catch(() => null);
        if (cfg && cfg.APP_API_KEY) headers['X-App-Key'] = cfg.APP_API_KEY;
    } catch {}
    return fetch(STOTT_API_BASE + path, { ...options, headers });
}

function stottShowLogin(message) {
    ['start-screen', 'game-screen', 'result-screen'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    });
    const login = document.getElementById('login-screen');
    if (login) login.classList.remove('hidden');
    if (message) {
        const err = document.getElementById('login-error');
        if (err) { err.innerText = message; err.classList.remove('hidden'); }
    }
    stottUpdateUserChip();
}

function stottShowApp() {
    const login = document.getElementById('login-screen');
    if (login) login.classList.add('hidden');
    const start = document.getElementById('start-screen');
    if (start) start.classList.remove('hidden');
    stottUpdateUserChip();
}

function stottUpdateUserChip() {
    const chip = document.getElementById('user-chip');
    if (!chip) return;
    if (stottUser) {
        chip.classList.remove('hidden');
        const name = document.getElementById('user-chip-name');
        if (name) name.innerText = stottUser.fullName || stottUser.login || '';
    } else {
        chip.classList.add('hidden');
    }
}

async function stottDoLogin(event) {
    if (event) event.preventDefault();
    const loginEl = document.getElementById('login-username');
    const passEl = document.getElementById('login-password');
    const btn = document.getElementById('login-btn');
    const err = document.getElementById('login-error');
    const login = (loginEl.value || '').trim().toLowerCase();
    const password = passEl.value || '';
    if (!login || !password) {
        err.innerText = '请输入用户名和密码。';
        err.classList.remove('hidden');
        return;
    }
    btn.disabled = true;
    btn.innerText = '登录中…';
    try {
        const res = await stottApi('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login, password }),
        });
        if (!res.ok) throw new Error('bad');
        const data = await res.json();
        stottSetToken(data.token);
        stottUser = data;
        passEl.value = '';
        err.classList.add('hidden');
        stottShowApp();
        stottStartHeartbeat();
        showToast('登录成功，欢迎回来！');
    } catch {
        err.innerText = '用户名或密码不正确，请重试。';
        err.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerText = '登 录';
    }
}

async function stottCheckSession() {
    const token = stottGetToken();
    if (!token) return false;
    try {
        const res = await stottApi('/session');
        if (!res.ok) return false;
        const data = await res.json();
        if (data.kicked) {
            stottForceLogout('此账号已在另一台设备登录，你已被登出。');
            return false;
        }
        if (data.ok) {
            stottUser = data;
            return true;
        }
        return false;
    } catch {
        // Network failure: stay logged in locally, retry next heartbeat.
        // (Login state is only revoked by an explicit kick or logout.)
        return !!stottUser;
    }
}

function stottStartHeartbeat() {
    stottStopHeartbeat();
    stottHeartbeatTimer = setInterval(async () => {
        const token = stottGetToken();
        if (!token) { stottStopHeartbeat(); return; }
        await stottCheckSession();
    }, STOTT_HEARTBEAT_MS);
}

function stottStopHeartbeat() {
    if (stottHeartbeatTimer) clearInterval(stottHeartbeatTimer);
    stottHeartbeatTimer = null;
}

async function stottLogout() {
    try {
        await stottApi('/logout', { method: 'POST' });
    } catch {}
    stottSetToken(null);
    stottUser = null;
    stottStopHeartbeat();
    stottShowLogin();
}

function stottForceLogout(message) {
    stottSetToken(null);
    stottUser = null;
    stottStopHeartbeat();
    try { if (document.getElementById('game-screen')) document.getElementById('game-screen').classList.add('hidden'); } catch {}
    stottShowLogin(message);
    showToast(message);
}

// On page load: a saved token skips the login screen (server re-verified).
document.addEventListener('DOMContentLoaded', async () => {
    const ok = await stottCheckSession();
    if (ok) {
        stottShowApp();
        stottStartHeartbeat();
    } else {
        stottSetToken(null);
        stottUser = null;
        stottShowLogin();
    }
});
