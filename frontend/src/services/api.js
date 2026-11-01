/**
 * Centralized API Client for CSE Attendance System
 */

const API_BASE_URL = ''; // Uses Vite proxy (or set to 'http://127.0.0.1:8000')

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.dispatchEvent(new Event('auth-expired'));
    throw new Error('Session expired. Please log in again.');
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data.detail || data.message || `Request failed with status ${response.status}`;
    throw new Error(errorMsg);
  }

  return data;
}

export const authApi = {
  login: (username, password) =>
    apiRequest('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  getMe: () => apiRequest('/me'),
};

export const teacherApi = {
  getMyCourses: () => apiRequest('/teacher/my-courses'),
  submitAttendance: (payload) =>
    apiRequest('/attendance/submit', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  modifyAttendance: (payload) =>
    apiRequest('/attendance/modify', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
};

export const tgApi = {
  getMyStudents: () => apiRequest('/tg/my-students'),
  getAttendanceReport: () => apiRequest('/tg/attendance-report'),
  getAlerts: () => apiRequest('/tg/alerts'),
  markAlertRead: (alertId) =>
    apiRequest(`/tg/alerts/${alertId}/read`, {
      method: 'PATCH',
    }),
};

export const studentApi = {
  getMyAttendance: () => apiRequest('/student/my-attendance'),
};

export const reportsApi = {
  getDivisionReport: (divId) => apiRequest(`/reports/division/${divId}`),
  downloadCsv: async (divId) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`/reports/division/${divId}/export-csv`, {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    if (!res.ok) throw new Error('Failed to export CSV report');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Attendance_Report_${divId}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },
};

export const auditApi = {
  getLogs: () => apiRequest('/audit-trail'),
};

export const alertsApi = {
  triggerCheck: () =>
    apiRequest('/alerts/trigger-check', {
      method: 'POST',
    }),
};

