const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  try {
    const response = await fetch(url, { ...options, headers });
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.detail?.message || data?.detail || data?.message || `Request failed with status ${response.status}`;
      const err = new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      err.status = response.status;
      err.data = data;
      throw err;
    }
    return data;
  } catch (err) {
    if (!err.status) {
      // Network or fetch error
      err.message = err.message || 'Network error: Unable to reach SafePlate server.';
    }
    throw err;
  }
}

export const api = {
  // System Health & AI status
  getHealth: () => request('/health'),

  // User Profile
  getProfile: () => request('/profile'),
  updateProfile: (data) => request('/profile', { method: 'PUT', body: JSON.stringify(data) }),

  // Pantry
  getPantry: () => request('/pantry'),
  addPantryItem: (data) => request('/pantry', { method: 'POST', body: JSON.stringify(data) }),
  deletePantryItem: (id) => request(`/pantry/${id}`, { method: 'DELETE' }),

  // Meal Planning & Agent
  getMealPlan: () => request('/meal-plan'),
  generateMealPlan: (params = {}) => request('/meal-plan/generate', { method: 'POST', body: JSON.stringify(params) }),
  getAgentRun: (runId) => request(`/agent/runs/${runId}`),

  // Safety & "Can I Eat This?"
  checkSafety: (query) => request('/safety/check', { method: 'POST', body: JSON.stringify({ query }) }),
  substituteIngredient: (ingredient) => request('/meal/substitute', { method: 'POST', body: JSON.stringify({ ingredient }) }),
};
