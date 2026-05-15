const API_BASE = '';

async function request(method, path, body = null) {
    const token = getToken();
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    };
    if (body !== null) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${path}`, opts);
    if (res.status === 401) {
        removeToken();
        showToast('인증이 만료되었습니다. 다시 로그인해주세요.', 'error');
        setTimeout(() => location.href = '/login.html', 1500);
        return null;
    }
    const data = res.status === 204 ? null : await res.json();
    if (!res.ok) {
        const msg = data?.error?.message || '오류가 발생했습니다';
        throw { status: res.status, code: data?.error?.code, message: msg };
    }
    return data;
}

const api = {
    get: (path) => request('GET', path),
    post: (path, body) => request('POST', path, body),
    put: (path, body) => request('PUT', path, body),
    patch: (path, body) => request('PATCH', path, body),
    del: (path) => request('DELETE', path),
};

function showToast(msg, type = 'info') {
    let el = document.getElementById('toast');
    if (!el) {
        el = document.createElement('div');
        el.id = 'toast';
        el.className = 'fixed bottom-4 right-4 px-4 py-2 rounded shadow text-white z-50 transition-all';
        document.body.appendChild(el);
    }
    el.textContent = msg;
    el.className = `fixed bottom-4 right-4 px-4 py-2 rounded shadow text-white z-50 ${type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green-500' : 'bg-gray-700'}`;
    el.style.display = 'block';
    clearTimeout(el._t);
    el._t = setTimeout(() => el.style.display = 'none', 3000);
}

function showConfirm(msg) {
    return new Promise(resolve => resolve(confirm(msg)));
}
