/**
 * BrainFeed API Client & Data Collection Layer
 * Manages all communication with the ML backend.
 */

const BrainFeedAPI = (() => {
    const BASE_URL = window.location.origin;

    // --- User Session Management ---
    function getUser() {
        const raw = localStorage.getItem('brainfeed_user');
        return raw ? JSON.parse(raw) : null;
    }

    function setUser(user) {
        localStorage.setItem('brainfeed_user', JSON.stringify(user));
    }

    function clearUser() {
        localStorage.removeItem('brainfeed_user');
        localStorage.removeItem('brainfeed_session');
    }

    function getSessionId() {
        return localStorage.getItem('brainfeed_session');
    }

    function setSessionId(id) {
        localStorage.setItem('brainfeed_session', id);
    }

    // --- API Helper ---
    async function apiFetch(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        const config = {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        };
        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }
        const response = await fetch(url, config);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        return data;
    }

    // --- Auth ---
    async function register(name, email, password, department, targetExams) {
        const data = await apiFetch('/api/auth/register', {
            method: 'POST',
            body: { name, email, password, department, targetExams }
        });
        if (data.success) setUser(data.user);
        return data;
    }

    async function login(email, password) {
        const data = await apiFetch('/api/auth/login', {
            method: 'POST',
            body: { email, password }
        });
        if (data.success) setUser(data.user);
        return data;
    }

    function logout() {
        const sessionId = getSessionId();
        if (sessionId) endSession(sessionId).catch(() => { });
        clearUser();
    }

    // --- Sessions ---
    async function startSession(userId) {
        const data = await apiFetch('/api/sessions/start', {
            method: 'POST',
            body: { userId, deviceType: detectDevice() }
        });
        if (data.sessionId) setSessionId(data.sessionId);
        return data;
    }

    async function endSession(sessionId) {
        return apiFetch('/api/sessions/end', {
            method: 'POST',
            body: { sessionId }
        });
    }

    // --- Questions ---
    async function fetchFeed(category) {
        const user = getUser();
        const userId = user?.id || '';
        const sessionId = getSessionId() || '';
        let url = `/api/questions/feed?limit=5&userId=${userId}&sessionId=${sessionId}`;
        if (category && category !== 'All') url += `&category=${encodeURIComponent(category)}`;
        return apiFetch(url);
    }

    async function submitAnswer(questionId, selectedOption, responseTime) {
        const user = getUser();
        if (!user) throw new Error('Not logged in');
        return apiFetch('/api/questions/submit', {
            method: 'POST',
            body: {
                userId: user.id,
                questionId,
                selectedOption,
                responseTime,
                sessionId: getSessionId() || null
            }
        });
    }

    // --- Analytics ---
    async function fetchAnalytics() {
        const user = getUser();
        if (!user) throw new Error('Not logged in');
        return apiFetch(`/api/analytics/dashboard?userId=${user.id}`);
    }

    // --- Utilities ---
    function detectDevice() {
        const w = window.innerWidth;
        if (w < 768) return 'mobile';
        if (w < 1024) return 'tablet';
        return 'desktop';
    }

    function isLoggedIn() {
        return !!getUser();
    }

    // --- Timer for response time tracking ---
    let questionStartTime = null;

    function startTimer() {
        questionStartTime = Date.now();
    }

    function getElapsedTime() {
        if (!questionStartTime) return 0;
        return (Date.now() - questionStartTime) / 1000;
    }

    // --- Initialize session on page load ---
    async function initSession() {
        const user = getUser();
        if (user && !getSessionId()) {
            try { await startSession(user.id); } catch (e) { console.warn('Session start failed:', e); }
        }
    }

    // --- Streak sync across pages ---
    function updateStreakDisplay(streak) {
        const el = document.getElementById('streak-score');
        if (el) el.innerText = streak;
        localStorage.setItem('brainfeed_streak', streak);
    }

    function getStoredStreak() {
        return parseInt(localStorage.getItem('brainfeed_streak') || '0');
    }

    return {
        register, login, logout, getUser, isLoggedIn,
        startSession, endSession, initSession,
        fetchFeed, submitAnswer,
        fetchAnalytics,
        startTimer, getElapsedTime,
        updateStreakDisplay, getStoredStreak,
        setUser, getSessionId
    };
})();

// Auto-init session on page load
document.addEventListener('DOMContentLoaded', () => {
    BrainFeedAPI.initSession();
    // Sync streak across pages
    const streakEl = document.getElementById('streak-score');
    if (streakEl && !streakEl.dataset.dynamic) {
        streakEl.innerText = BrainFeedAPI.getStoredStreak();
    }
});
