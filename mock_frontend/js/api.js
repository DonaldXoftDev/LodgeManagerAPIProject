const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Unified fetch wrapper
async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // If options.body is FormData (e.g. for OAuth2 login), let browser set Content-Type
    if (options.body instanceof URLSearchParams) {
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
    }

    const config = {
        ...options,
        headers
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        if (response.status === 401) {
            // Unauthorized - token expired or missing
            localStorage.removeItem('access_token');
            if (!window.location.pathname.endsWith('auth.html') && !window.location.pathname.endsWith('tenant-register.html')) {
                window.location.href = 'auth.html';
            }
            throw new Error('Session expired. Please log in again.');
        }

        // 204 No Content has no JSON body
        if (response.status === 204) {
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            let errorMsg = data.detail || 'An API error occurred';
            if (Array.isArray(data.detail)) {
                // FastAPI Validation Error formatting
                errorMsg = data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
            }
            throw new Error(errorMsg);
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function showToast(message) {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}
