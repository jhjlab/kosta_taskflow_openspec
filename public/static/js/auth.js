const TOKEN_KEY = 'taskflow_token';
const USER_KEY = 'taskflow_user';

function saveToken(token) { localStorage.setItem(TOKEN_KEY, token); }
function getToken() { return localStorage.getItem(TOKEN_KEY); }
function removeToken() { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); }
function isLoggedIn() { return !!getToken(); }

function saveUser(user) { localStorage.setItem(USER_KEY, JSON.stringify(user)); }
function getCurrentUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
}

function requireAuth() {
    if (!isLoggedIn()) { location.href = '/login.html'; return false; }
    return true;
}

function requireNoTeam() {
    const user = getCurrentUser();
    if (user && user.team_id) { location.href = '/kanban.html'; return false; }
    return true;
}
