import axios from 'axios';

const pythonApiBaseUrl = import.meta.env.VITE_PYTHON_API_URL || 'http://localhost:8000';
const nodeApiBaseUrl = import.meta.env.VITE_NODE_API_URL || 'http://localhost:5000';

export const pythonAPI = axios.create({
  baseURL: pythonApiBaseUrl,
});

export const nodeAPI = axios.create({
  baseURL: nodeApiBaseUrl,
});

pythonAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('algocoach_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

pythonAPI.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('algocoach_token');
      localStorage.removeItem('algocoach_user');
    }

    return Promise.reject(error);
  },
);
