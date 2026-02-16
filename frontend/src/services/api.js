/**
 * API service for making HTTP requests to the backend.
 */
import axios from 'axios';
import { auth } from './firebase';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add Firebase auth token
api.interceptors.request.use(
  async (config) => {
    // Get current user from Firebase
    const user = auth.currentUser;

    if (user) {
      try {
        // Get Firebase ID token
        const idToken = await user.getIdToken();

        // Add Authorization header
        config.headers.Authorization = `Bearer ${idToken}`;
      } catch (error) {
        console.error('Error getting auth token:', error);
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle specific error codes
      if (error.response.status === 401) {
        // Unauthorized - redirect to login
        console.error('Unauthorized. Please login again.');
        // You can dispatch a logout action here
      } else if (error.response.status === 403) {
        console.error('Forbidden. You do not have permission.');
      } else if (error.response.status === 500) {
        console.error('Server error. Please try again later.');
      }
    } else if (error.request) {
      console.error('No response from server. Check your connection.');
    } else {
      console.error('Error setting up request:', error.message);
    }

    return Promise.reject(error);
  }
);

/**
 * API endpoints
 */
export const apiService = {
  // Health check
  health: () => api.get('/health'),

  // Activities
  getActivities: (params = {}) => api.get('/api/activities', { params }),
  getActivityStats: () => api.get('/api/activities/stats'),
  getActivity: (id) => api.get(`/api/activities/${id}`),

  // Threats/Alerts
  getThreats: (params = {}) => api.get('/api/threats', { params }),
  getThreatStats: () => api.get('/api/threats/stats'),
  acknowledgeThreat: (alertId) => api.post('/api/threats/acknowledge', { alert_id: alertId }),
  getThreat: (id) => api.get(`/api/threats/${id}`),

  // File Scanning
  scanFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/scan-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getScanResults: (params = {}) => api.get('/api/scan-results', { params }),
  getScanStats: () => api.get('/api/scan-results/stats'),
  getScanResult: (id) => api.get(`/api/scan-results/${id}`),

  // Reports
  getSummary: () => api.get('/api/reports/summary'),
  getActivitiesTimeline: (days = 7) => api.get('/api/reports/activities-timeline', { params: { days } }),

  // ML Models
  trainModels: () => api.post('/api/models/train'),
  getModelMetrics: (limit = 10) => api.get('/api/models/metrics', { params: { limit } }),
  getLatestMetrics: () => api.get('/api/models/metrics/latest'),
  getModelStatus: () => api.get('/api/models/status'),
};

export default api;
