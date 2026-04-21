export const logger = {
  info: (tag, ...args) => __DEV__ && console.log(`ℹ️ [${tag}]`, ...args),
  warn: (tag, ...args) => __DEV__ && console.warn(`⚠️ [${tag}]`, ...args),
  error: (tag, ...args) => __DEV__ && console.error(`❌ [${tag}]`, ...args),
  api: (method, url, config, response) => {
    if (!__DEV__) return;
    console.group(`🌐 API ${method?.toUpperCase() || 'UNKNOWN'} ${url || ''}`);
    // if (config?.headers) console.log('🔑 Headers:', config.headers);
    if (config?.data) {
      const data = typeof config.data === 'string' 
        ? config.data.substring(0, 150) + (config.data.length > 150 ? '...' : '')
        : config.data;
      console.log('📦 Payload:', data);
    }
    if (response) console.log('✅ Response:', response.status);
    console.groupEnd();
  }
};