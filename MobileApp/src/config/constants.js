import { Platform } from 'react-native';

const getApiHost = () => {
  if (process.env.EXPO_PUBLIC_API_HOST) return process.env.EXPO_PUBLIC_API_HOST;
  if (Platform.OS === 'web') return process.env.EXPO_PUBLIC_API_HOST_WEB || 'localhost';
  if (Platform.OS === 'android') return process.env.EXPO_PUBLIC_API_HOST_ANDROID || '10.0.2.2';
  if (Platform.OS === 'ios') return process.env.EXPO_PUBLIC_API_HOST_IOS || 'localhost';
  return process.env.EXPO_PUBLIC_API_HOST_DEVICE || '192.168.1.100';
};

const API_HOST = getApiHost();
const AUTH_PORT = process.env.EXPO_PUBLIC_AUTH_SERVICE_PORT || '8001';
const DEFECTS_PORT = process.env.EXPO_PUBLIC_DEFECTS_SERVICE_PORT || '8002';

export const AUTH_SERVICE_URL = `http://${API_HOST}:${AUTH_PORT}`;
export const DEFECTS_SERVICE_URL = `http://${API_HOST}:${DEFECTS_PORT}`;

if (__DEV__) {
  console.log('🌍 API Config:', { platform: Platform.OS, host: API_HOST, authUrl: AUTH_SERVICE_URL });
}