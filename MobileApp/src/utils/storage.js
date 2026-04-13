import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const isWeb = Platform.OS === 'web';

export const storage = {
  // 🔹 Всегда возвращаем Promise для совместимости с async interceptors
  getItem: async (key) => {
    if (isWeb) {
      try {
        return Promise.resolve(localStorage.getItem(key));
      } catch (e) {
        console.warn('localStorage getItem error:', e);
        return Promise.resolve(null);
      }
    }
    return SecureStore.getItemAsync(key);
  },
  setItem: async (key, value) => {
    if (isWeb) {
      try {
        localStorage.setItem(key, value);
        return Promise.resolve();
      } catch (e) {
        console.warn('localStorage setItem error:', e);
        return Promise.reject(e);
      }
    }
    return SecureStore.setItemAsync(key, value);
  },
  removeItem: async (key) => {
    if (isWeb) {
      try {
        localStorage.removeItem(key);
        return Promise.resolve();
      } catch (e) {
        console.warn('localStorage removeItem error:', e);
        return Promise.reject(e);
      }
    }
    return SecureStore.deleteItemAsync(key);
  },
};