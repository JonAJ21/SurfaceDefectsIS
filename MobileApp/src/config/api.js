import axios from 'axios';
import { storage } from '../utils/storage';
import { AUTH_SERVICE_URL, DEFECTS_SERVICE_URL } from './constants';
import { logger } from '../utils/logger';

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => error ? prom.reject(error) : prom.resolve(token));
  failedQueue = [];
};

export const rawApi = axios.create({ baseURL: AUTH_SERVICE_URL, timeout: 15000 });

rawApi.interceptors.request.use(config => {
  logger.info('RAW_API', `${config.method?.toUpperCase()} ${config.url}`);
  return config;
});
rawApi.interceptors.response.use(res => res, err => Promise.reject(err));

export function createApiInstance(baseURL) {
  const api = axios.create({ baseURL, timeout: 15000 });

  api.interceptors.request.use(async (config) => {
    const token = await storage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    
    // 🔹 Не переопределяем Content-Type, если отправляем FormData (axios сам поставит boundary)
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }
    
    logger.api(config.method, config.url, config);
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      const isAuthEndpoint = originalRequest?.url?.includes('/v1/users/login') || 
                             originalRequest?.url?.includes('/v1/users/register') ||
                             originalRequest?.url?.includes('/v1/users/me/refresh');

      if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthEndpoint) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => failedQueue.push({ resolve, reject }))
            .then(token => { originalRequest.headers.Authorization = `Bearer ${token}`; return api(originalRequest); });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const refreshToken = await storage.getItem('refresh_token');
          if (!refreshToken) throw new Error('No refresh token');

          const formData = new URLSearchParams();
          formData.append('refresh_token', refreshToken);

          const { data } = await rawApi.post('/v1/users/me/refresh', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
          });

          await storage.setItem('access_token', data.access_token);
          if (data.refresh_token) await storage.setItem('refresh_token', data.refresh_token);

          processQueue(null, data.access_token);
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          await storage.removeItem('access_token');
          await storage.removeItem('refresh_token');
          if (typeof window !== 'undefined' && window.dispatchEvent) window.dispatchEvent(new Event('auth:session_expired'));
          return Promise.reject(refreshError);
        } finally { isRefreshing = false; }
      }
      return Promise.reject(error);
    }
  );

  return api;
}

export const authApi = createApiInstance(AUTH_SERVICE_URL);
export const defectsApi = createApiInstance(DEFECTS_SERVICE_URL);