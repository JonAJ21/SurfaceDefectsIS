import React, { createContext, useContext, useState, useEffect } from 'react';
import { Platform } from 'react-native';
import { authApi, rawApi } from '../config/api';
import { storage } from '../utils/storage';
import { logger } from '../utils/logger';

const AuthContext = createContext(null);

const formatFastAPIError = (detail) => {
  if (!Array.isArray(detail)) return typeof detail === 'string' ? detail : 'Ошибка сервера';
  const fieldMap = { username: 'Логин/Email', email: 'Email', password: 'Пароль', password_confirm: 'Подтверждение пароля' };
  return detail.map(err => {
    const field = err.loc?.[err.loc.length - 1] || 'field';
    return `${fieldMap[field] || field}: ${err.msg}`;
  }).join('\n');
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const fetchCurrentSession = async () => {
    try {
      const { data } = await authApi.get('/v1/users/me/session');
      return data;
    } catch (err) {
      logger.warn('AUTH', 'Failed to fetch current session', err.message);
      return null;
    }
  };

  const fetchUserProfile = async () => {
    try {
      const { data } = await authApi.get('/v1/users/me', {
        params: { load_roles: true, load_permissions: true, load_sessions: true }
      });
      const currentSessionData = await fetchCurrentSession();
      const userData = { ...data, currentSessionOid: currentSessionData?.session_oid || null };
      setUser(userData);
      setIsAuthenticated(true);
      return userData;
    } catch (err) {
      // Если 401, пробуем обновить токен
      if (err.response?.status === 401) {
        try {
          const refreshToken = await storage.getItem('refresh_token');
          if (refreshToken) {
            const formData = new FormData();
            formData.append('refresh_token', refreshToken);
            
            const { data } = await rawApi.post('/v1/users/me/refresh', formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            await storage.setItem('access_token', data.access_token);
            if (data.refresh_token) await storage.setItem('refresh_token', data.refresh_token);
            
            // Повторяем запрос профиля с новым токеном
            return fetchUserProfile();
          }
        } catch (refreshErr) {
          console.error('Refresh failed:', refreshErr);
          await storage.removeItem('access_token');
          await storage.removeItem('refresh_token');
        }
      }
      setUser(null);
      setIsAuthenticated(false);
      return null;
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        const refreshToken = await storage.getItem('refresh_token');
        if (refreshToken) await fetchUserProfile();
        else setIsAuthenticated(false);
      } catch (e) { logger.warn('AUTH', 'Init failed', e); setIsAuthenticated(false); }
      finally { setLoading(false); }
    };
    init();

    let cleanup = () => {};
    if (Platform.OS === 'web' && typeof window !== 'undefined' && window.addEventListener) {
      const handleExpired = () => { setUser(null); setIsAuthenticated(false); setApiError('Сессия истекла.'); };
      window.addEventListener('auth:session_expired', handleExpired);
      cleanup = () => window.removeEventListener('auth:session_expired', handleExpired);
    }
    return cleanup;
  }, []);

  const clearMessages = () => { setApiError(null); setSuccessMessage(null); };

  const login = async (credentials) => {
    setLoading(true); clearMessages();
    try {
      // 🔹 Используем rawApi (без глобальных настроек JSON)
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);
      
      const { data } = await rawApi.post('/v1/users/login', formData.toString(), {
        headers: { 
          'Content-Type': 'application/x-www-form-urlencoded' 
        }
      });
      
      await storage.setItem('access_token', data.access_token);
      if (data.refresh_token) await storage.setItem('refresh_token', data.refresh_token);
      await fetchUserProfile();
      return data;
    } catch (error) {
      const msg = error.response?.data?.detail || error.message || 'Ошибка входа';
      setApiError(formatFastAPIError(msg));
      throw error;
    } finally { setLoading(false); }
  };

  const register = async (data) => {
    setLoading(true); clearMessages();
    try {
      // 🔹 Исправление 2: Безопасная обработка ответа без сложной деструктуризации
      const response = await authApi.post('/v1/users/register', data);
      // Поддержка и response.data (стандартный axios) и response (если есть интерцептор)
      const regData = response.data || response; 
      
      // 🔹 Исправление 3: Убрали проверку is_verified, которая ломала код, 
      // так как в вашем API это поле есть, но мы не будем на нем зацикливаться.
      setSuccessMessage('Аккаунт создан! Выполняем вход...');
      
      await login({ username: data.email, password: data.password });
    } catch (error) {
      const msg = error.response?.data?.detail || error.message || 'Ошибка регистрации';
      setApiError(formatFastAPIError(msg));
      throw error;
    } finally { setLoading(false); }
  };

  const verifyEmail = async () => {
    setLoading(true); clearMessages();
    try {
      await authApi.post('/v1/users/me/verify-by-email');
      setSuccessMessage('Письмо отправлено.');
      await fetchUserProfile();
    } catch (error) {
      setApiError(formatFastAPIError(error.response?.data?.detail || 'Ошибка'));
    } finally { setLoading(false); }
  };

  const logout = async (allSessions = false) => {
    const token = await storage.getItem('access_token');
    setUser(null); setIsAuthenticated(false); clearMessages();
    try {
      await Promise.all([storage.removeItem('access_token'), storage.removeItem('refresh_token')]);
    } catch (e) { console.error('Storage clear error', e); }
    if (token) {
      const endpoint = allSessions ? '/v1/users/me/logout-all' : '/v1/users/me/logout';
      rawApi.delete(endpoint, { headers: { Authorization: `Bearer ${token}` } }).catch(() => {});
    }
  };

  const userRoles = user?.roles?.map(r => r.name?.toLowerCase()) || [];
  const isAdmin = userRoles.includes('admin');
  const isModerator = userRoles.includes('moderator');
  // 🔹 Безопасный доступ (не ломает приложение, если поля нет)
  const isVerified = user?.is_verified ?? false;

  return (
    <AuthContext.Provider value={{ 
      user, isAuthenticated, loading, apiError, successMessage, 
      login, register, logout, verifyEmail, fetchUserProfile, 
      isAdmin, isModerator, isVerified
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};