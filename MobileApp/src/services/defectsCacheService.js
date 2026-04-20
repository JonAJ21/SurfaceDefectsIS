// MobileApp/src/services/defectsCacheService.js
import { defectsApi } from '../config/api';
import { logger } from '../utils/logger';

// Конфигурация
const CONFIG = {
  // Время жизни кэша (10 минут)
  CACHE_TTL: 10 * 60 * 1000,
  // Задержка после движения перед загрузкой (1 секунда)
  IDLE_DELAY: 1000,
  // Минимальное расстояние для обновления (100 метров)
  MIN_DISTANCE_UPDATE: 100,
  // Минимальное изменение зума для обновления
  MIN_ZOOM_CHANGE: 1,
  // Максимальное количество дефектов за запрос
  MAX_LIMIT: 1000,
  // Размер сетки для кэширования (0.01 градуса ≈ 1.1 км)
  GRID_SIZE: 0.01,
};

// Цвета для уровней опасности
export const SEVERITY_COLORS = {
  critical: '#dc2626', // Красный
  high: '#f97316',     // Оранжевый
  medium: '#f59e0b',   // Жёлтый
  low: '#22c55e',      // Зелёный
};

class DefectsCache {
  constructor() {
    this.cache = new Map();
    this.pendingRequests = new Map();
  }

  getGridKey(lat, lng) {
    const latCell = Math.floor(lat / CONFIG.GRID_SIZE);
    const lngCell = Math.floor(lng / CONFIG.GRID_SIZE);
    return `${latCell},${lngCell}`;
  }

  getBoundsKey(bounds) {
    const minLatCell = Math.floor(bounds.min_latitude / CONFIG.GRID_SIZE);
    const maxLatCell = Math.floor(bounds.max_latitude / CONFIG.GRID_SIZE);
    const minLngCell = Math.floor(bounds.min_longitude / CONFIG.GRID_SIZE);
    const maxLngCell = Math.floor(bounds.max_longitude / CONFIG.GRID_SIZE);
    return `${minLatCell},${maxLatCell},${minLngCell},${maxLngCell}`;
  }

  get(bounds) {
    const key = this.getBoundsKey(bounds);
    const cached = this.cache.get(key);
    
    if (cached && (Date.now() - cached.timestamp) < CONFIG.CACHE_TTL) {
      return cached.data;
    }
    
    if (cached) {
      this.cache.delete(key);
    }
    
    return null;
  }

  set(bounds, data) {
    const key = this.getBoundsKey(bounds);
    
    // Ограничиваем размер кэша
    if (this.cache.size > 100) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
    
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      bounds
    });
  }

  hasPending(bounds) {
    const key = this.getBoundsKey(bounds);
    return this.pendingRequests.has(key);
  }

  addPending(bounds, promise) {
    const key = this.getBoundsKey(bounds);
    this.pendingRequests.set(key, promise);
    promise.finally(() => {
      this.pendingRequests.delete(key);
    });
  }

  clear() {
    this.cache.clear();
    this.pendingRequests.clear();
  }

  getStats() {
    let activeCount = 0;
    const now = Date.now();
    for (const value of this.cache.values()) {
      if ((now - value.timestamp) < CONFIG.CACHE_TTL) {
        activeCount++;
      }
    }
    return {
      totalSize: this.cache.size,
      activeCount,
      ttlMinutes: CONFIG.CACHE_TTL / (60 * 1000)
    };
  }
}

class DefectsLoader {
  constructor() {
    this.cache = new DefectsCache();
    this.currentBounds = null;
    this.currentZoom = 16;
    this.subscribers = new Set();
    this.loadTimeout = null;
    this.lastLoadTime = 0;
    this.isLoading = false;
  }

  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  notify(data) {
    this.subscribers.forEach(callback => callback(data));
  }

  // Оптимизированная загрузка с debounce
  requestLoad(bounds, zoom, immediate = false) {
    if (!bounds) return;
    
    // Очищаем предыдущий таймаут
    if (this.loadTimeout) {
      clearTimeout(this.loadTimeout);
    }
    
    if (immediate) {
      this.loadDefects(bounds, zoom);
    } else {
      this.loadTimeout = setTimeout(() => {
        this.loadDefects(bounds, zoom);
      }, CONFIG.IDLE_DELAY);
    }
  }

  async loadDefects(bounds, zoom, force = false) {
    if (!bounds || this.isLoading) return;
    
    // Проверяем, нужно ли обновлять
    const now = Date.now();
    const timeSinceLastLoad = now - this.lastLoadTime;
    
    if (!force && timeSinceLastLoad < 3000 && !this.hasBoundsChanged(bounds)) {
      return;
    }
    
    // Проверяем кэш
    if (!force) {
      const cached = this.cache.get(bounds);
      if (cached) {
        this.notify({ type: 'cached', defects: cached, bounds, zoom });
        this.currentBounds = bounds;
        this.currentZoom = zoom;
        return cached;
      }
    }
    
    // Проверяем, нет ли уже такого запроса
    if (this.cache.hasPending(bounds)) {
      return;
    }
    
    this.isLoading = true;
    this.lastLoadTime = now;
    this.currentBounds = bounds;
    this.currentZoom = zoom;
    
    this.notify({ type: 'loading' });
    
    const promise = this._doLoad(bounds, zoom);
    this.cache.addPending(bounds, promise);
    
    try {
      const defects = await promise;
      this.cache.set(bounds, defects);
      this.notify({ type: 'loaded', defects, bounds, zoom });
      return defects;
    } catch (error) {
      console.error('Load defects error:', error);
      this.notify({ type: 'error', error });
      return [];
    } finally {
      this.isLoading = false;
    }
  }

  async _doLoad(bounds, zoom) {
    try {
      const { min_latitude, max_latitude, min_longitude, max_longitude } = bounds;
      
      // Адаптивный лимит в зависимости от зума
      let limit = CONFIG.MAX_LIMIT;
      if (zoom >= 16) limit = 500;
      if (zoom >= 18) limit = 200;
      
      const response = await defectsApi.get('/v1/defects/viewport/', {
        params: {
          min_longitude,
          min_latitude,
          max_longitude,
          max_latitude,
          limit
        },
        timeout: 15000
      });
      
      const data = response.data || [];
      
      // Форматируем дефекты с цветом в зависимости от опасности
      const formattedDefects = data.map(d => {
        // Определяем координаты
        let coords = d.snapped_coordinates || d.original_coordinates;
        let isLine = false;
        let coordinates = null;
        let centerLat = null;
        let centerLon = null;
        
        if (coords && Array.isArray(coords)) {
          // Линейный дефект - массив точек
          if (coords.length >= 2 && Array.isArray(coords[0]) && coords[0].length === 2) {
            isLine = true;
            coordinates = coords;
            centerLat = coords[0][1];
            centerLon = coords[0][0];
          }
          // Точечный дефект - [lng, lat]
          else if (coords.length === 2 && typeof coords[0] === 'number') {
            isLine = false;
            centerLat = coords[1];
            centerLon = coords[0];
          }
          // Точечный дефект - [[lng, lat]]
          else if (coords.length === 1 && Array.isArray(coords[0]) && coords[0].length === 2) {
            isLine = false;
            centerLat = coords[0][1];
            centerLon = coords[0][0];
          }
        }
        
        // Цвет в зависимости от severity
        const color = SEVERITY_COLORS[d.severity] || SEVERITY_COLORS.low;
        
        return {
          id: d.id,
          lat: centerLat,
          lon: centerLon,
          coordinates: coordinates,
          geometry_type: isLine ? 'linestring' : 'point',
          defect_type: d.defect_type,
          severity: d.severity,
          description: d.description || '',
          status: d.status,
          road_name: d.road_name,
          created_at: d.created_at,
          color: color
        };
      }).filter(d => {
        if (d.geometry_type === 'linestring') {
          return d.coordinates && d.coordinates.length >= 2;
        }
        return d.lat && d.lon;
      });
      
      console.log(`📊 Loaded ${formattedDefects.length} defects (${formattedDefects.filter(d => d.geometry_type === 'linestring').length} lines, ${formattedDefects.filter(d => d.geometry_type === 'point').length} points)`);
      
      return formattedDefects;
      
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  }

  hasBoundsChanged(newBounds) {
    if (!this.currentBounds) return true;
    
    const old = this.currentBounds;
    const newB = newBounds;
    
    const latDiff = Math.abs((old.min_latitude + old.max_latitude) - (newB.min_latitude + newB.max_latitude));
    const lngDiff = Math.abs((old.min_longitude + old.max_longitude) - (newB.min_longitude + newB.max_longitude));
    
    return latDiff > 0.02 || lngDiff > 0.02;
  }

  getCacheStats() {
    return this.cache.getStats();
  }

  clearCache() {
    this.cache.clear();
    console.log('🗑️ Cache cleared');
  }
}

export const defectsLoader = new DefectsLoader();
export { SEVERITY_COLORS };