/**
 * Mintuu AI — Auth Client
 * Handles signup, login, token management, and session persistence.
 */

const API = '';

// ── Token Management ──────────────────────────────
function setTokens(access, refresh) {
    localStorage.setItem('mintuu_access_token', access);
    localStorage.setItem('mintuu_refresh_token', refresh);
}
function getAccessToken() { return localStorage.getItem('mintuu_access_token'); }
function getRefreshToken() { return localStorage.getItem('mintuu_refresh_token'); }
function clearTokens() { localStorage.removeItem('mintuu_access_token'); localStorage.removeItem('mintuu_refresh_token'); localStorage.removeItem('mintuu_user'); }

function setUser(user) { localStorage.setItem('mintuu_user', JSON.stringify(user)); }
function getUser() { try { return JSON.parse(localStorage.getItem('mintuu_user')); } catch { return null; } }

function isLoggedIn() { return !!getAccessToken(); }

// ── Auth API Calls ────────────────────────────────
async function authFetch(url, options = {}) {
    const token = getAccessToken();
    if (token) {
        options.headers = options.headers || {};
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(url, options);
    if (res.status === 401) {
        // Try refresh
        const refreshed = await tryRefreshToken();
        if (refreshed) {
            options.headers['Authorization'] = `Bearer ${getAccessToken()}`;
            return fetch(url, options);
        } else {
            clearTokens();
            window.location.href = '/login';
            return res;
        }
    }
    return res;
}

async function tryRefreshToken() {
    const refresh = getRefreshToken();
    if (!refresh) return false;
    try {
        const res = await fetch(`${API}/auth/refresh`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${refresh}` },
        });
        if (!res.ok) return false;
        const data = await res.json();
        localStorage.setItem('mintuu_access_token', data.access_token);
        return true;
    } catch { return false; }
}

// ── Signup Handler ────────────────────────────────
async function handleSignup(e) {
    e.preventDefault();
    const errEl = document.getElementById('signup-error');
    const btn = document.getElementById('signup-btn');
    errEl.classList.remove('visible');
    btn.disabled = true;
    btn.textContent = 'Creating account...';

    const form = document.getElementById('signup-form');
    const body = {
        full_name: form.querySelector('#full-name').value.trim(),
        email: form.querySelector('#email').value.trim(),
        password: form.querySelector('#password').value,
        confirm_password: form.querySelector('#confirm-password').value,
    };

    if (body.password !== body.confirm_password) {
        showError(errEl, 'Passwords do not match.');
        btn.disabled = false; btn.textContent = 'Create Account';
        return false;
    }
    if (body.password.length < 6) {
        showError(errEl, 'Password must be at least 6 characters.');
        btn.disabled = false; btn.textContent = 'Create Account';
        return false;
    }

    try {
        const res = await fetch(`${API}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!res.ok) {
            showError(errEl, data.detail || 'Signup failed. Please try again.');
            btn.disabled = false; btn.textContent = 'Create Account';
            return false;
        }
        setTokens(data.access_token, data.refresh_token);
        setUser(data.user);
        window.location.href = '/app';
    } catch (err) {
        showError(errEl, 'Network error. Please check your connection.');
        btn.disabled = false; btn.textContent = 'Create Account';
    }
    return false;
}

// ── Login Handler ─────────────────────────────────
async function handleLogin(e) {
    e.preventDefault();
    const errEl = document.getElementById('login-error');
    const btn = document.getElementById('login-btn');
    errEl.classList.remove('visible');
    btn.disabled = true;
    btn.textContent = 'Logging in...';

    const form = document.getElementById('login-form');
    const body = {
        email: form.querySelector('#email').value.trim(),
        password: form.querySelector('#password').value,
    };

    try {
        const res = await fetch(`${API}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!res.ok) {
            showError(errEl, data.detail || 'Invalid email or password.');
            btn.disabled = false; btn.textContent = 'Log In';
            return false;
        }
        setTokens(data.access_token, data.refresh_token);
        setUser(data.user);
        window.location.href = '/app';
    } catch (err) {
        showError(errEl, 'Network error. Please check your connection.');
        btn.disabled = false; btn.textContent = 'Log In';
    }
    return false;
}

function showError(el, msg) {
    el.textContent = msg;
    el.classList.add('visible');
}

function logout() {
    clearTokens();
    window.location.href = '/';
}

// ── Auto-redirect if already logged in ────────────
(function checkAuth() {
    const path = window.location.pathname;
    if ((path === '/login' || path === '/signup' || path === '/') && isLoggedIn()) {
        window.location.href = '/app';
    }
})();
