// MobileApp/src/utils/urlHelper.js
import { Platform } from 'react-native';
import { IS_DEV, LOCAL_STATIC_URL } from '../config/constants';

/**
 * Проверяет, является ли URL локальным (для development режима)
 */
const isLocalUrl = (url) => {
  if (!IS_DEV) return false;
  return url.includes('localhost') || url.includes('10.0.2.2') || url.includes('127.0.0.1');
};

/**
 * Нормализация URL для корректного отображения на Android в development режиме
 * В production режиме URL не изменяются (они уже полные и корректные от бэкенда)
 */
export const normalizePhotoUrl = (url) => {
  if (!url) return null;
  
  // В production режиме - возвращаем URL как есть (уже полный S3/MinIO URL)
  if (!IS_DEV) {
    return url;
  }
  
  // В development режиме - заменяем localhost на правильный хост для Android
  if (Platform.OS === 'android' && isLocalUrl(url)) {
    let normalized = url.replace(/http:\/\/localhost/g, `http://${LOCAL_STATIC_URL.match(/http:\/\/([^:]+)/)?.[1] || '10.0.2.2'}`);
    normalized = normalized.replace(/https:\/\/localhost/g, `https://${LOCAL_STATIC_URL.match(/https:\/\/([^:]+)/)?.[1] || '10.0.2.2'}`);
    return normalized;
  }
  
  return url;
};

/**
 * Получение URL фото
 * - В production: возвращаем URL как есть (бэкенд отдаёт полный S3 URL)
 * - В development: нормализуем локальные URL для Android
 */
export const getPhotoUrl = (photoUrl) => {
  if (!photoUrl) return null;
  return normalizePhotoUrl(photoUrl);
};

/**
 * Получение URL аватара пользователя
 */
export const getAvatarUrl = (avatarUrl) => {
  if (!avatarUrl) return null;
  return normalizePhotoUrl(avatarUrl);
};