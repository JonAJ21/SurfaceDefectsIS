// MobileApp/src/config/constants.js
import { Platform } from 'react-native';

// Определяем окружение
export const IS_DEV = __DEV__;

// Получение хоста API для локальной разработки
const getLocalApiHost = () => {
  if (process.env.EXPO_PUBLIC_API_HOST) {
    return process.env.EXPO_PUBLIC_API_HOST;
  }
  
  if (Platform.OS === 'web') {
    return process.env.EXPO_PUBLIC_API_HOST_WEB || 'localhost';
  }
  
  if (Platform.OS === 'android') {
    // Для физического Android устройства
    if (process.env.EXPO_PUBLIC_API_HOST_DEVICE) {
      return process.env.EXPO_PUBLIC_API_HOST_DEVICE;
    }
    // Для эмулятора
    return process.env.EXPO_PUBLIC_API_HOST_ANDROID || '10.0.2.2';
  }
  
  if (Platform.OS === 'ios') {
    return process.env.EXPO_PUBLIC_API_HOST_IOS || 'localhost';
  }
  
  return 'localhost';
};

// Базовый URL для статических файлов (только для development)
const getLocalStaticUrl = () => {
  const host = getLocalApiHost();
  return `http://${host}:9000`;
};

// Экспортируем URL сервисов - теперь через nginx на порту 80
const API_HOST = getLocalApiHost();
const NGINX_PORT = process.env.EXPO_PUBLIC_NGINX_PORT || '80';

export const AUTH_SERVICE_URL = `http://${API_HOST}:${NGINX_PORT}/auth-service`;
export const DEFECTS_SERVICE_URL = `http://${API_HOST}:${NGINX_PORT}/defects-service`;
export const LOCAL_STATIC_URL = getLocalStaticUrl();

if (IS_DEV) {
  console.log('🔧 DEV Config:', { 
    platform: Platform.OS, 
    host: API_HOST,
    nginxPort: NGINX_PORT,
    authUrl: AUTH_SERVICE_URL,
    defectsUrl: DEFECTS_SERVICE_URL,
    staticUrl: LOCAL_STATIC_URL
  });
}