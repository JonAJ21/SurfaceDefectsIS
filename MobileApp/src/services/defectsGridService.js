// MobileApp/src/services/defectsGridService.js
import { defectsApi } from '../config/api';
import { proximityService } from './proximityService';

const CONFIG = {
  GRID_SIZE: 0.09,
  LOAD_RADIUS_CELLS: 1,
  PRELOAD_THRESHOLD: 0.3,
  IDLE_DELAY: 500,
  CELL_TTL: 10 * 60 * 1000,
};

export const SEVERITY_COLORS = {
  critical: '#dc2626',
  high: '#f97316',
  medium: '#f59e0b',
  low: '#22c55e',
};

class DefectsGridManager {
  constructor() {
    this.loadedCells = new Map();
    this.currentCenterCell = null;
    this.loadTimeout = null;
    this.subscribers = new Set();
    this.isLoading = false;
    this.currentZoom = 16;
  }

  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  notify(data) {
    this.subscribers.forEach(callback => callback(data));
  }

  getCellKey(lat, lng) {
    const latCell = Math.floor(lat / CONFIG.GRID_SIZE);
    const lngCell = Math.floor(lng / CONFIG.GRID_SIZE);
    return `${latCell},${lngCell}`;
  }

  getCellBounds(lat, lng) {
    const latCell = Math.floor(lat / CONFIG.GRID_SIZE);
    const lngCell = Math.floor(lng / CONFIG.GRID_SIZE);
    const min_latitude = latCell * CONFIG.GRID_SIZE;
    const max_latitude = min_latitude + CONFIG.GRID_SIZE;
    const min_longitude = lngCell * CONFIG.GRID_SIZE;
    const max_longitude = min_longitude + CONFIG.GRID_SIZE;
    return { min_latitude, max_latitude, min_longitude, max_longitude };
  }

  getCellCenter(lat, lng) {
    const bounds = this.getCellBounds(lat, lng);
    return {
      lat: (bounds.min_latitude + bounds.max_latitude) / 2,
      lng: (bounds.min_longitude + bounds.max_longitude) / 2
    };
  }

  async loadViewport(bounds, zoom) {
    const { min_latitude, max_latitude, min_longitude, max_longitude } = bounds;
    this.notify({ type: 'loading', area: 'viewport' });
    try {
      const limit = zoom < 12 ? 200 : 500;
      const response = await defectsApi.get('/v1/defects/viewport/', {
        params: { min_longitude, min_latitude, max_longitude, max_latitude, limit },
        timeout: 10000
      });
      const data = response.data || [];
      const formattedDefects = this.formatDefects(data);
      console.log('📡 Viewport loaded:', formattedDefects.length, 'defects');
      
      // ВСЕГДА обновляем proximityService
      if (formattedDefects.length > 0) {
        proximityService.updateDefectsCache(formattedDefects);
      }
      
      this.notify({ type: 'viewport_loaded', defects: formattedDefects, bounds, zoom });
      return formattedDefects;
    } catch (error) {
      console.error('Viewport load failed:', error);
      this.notify({ type: 'error', error });
      return [];
    }
  }

  async loadCell(lat, lng, zoom) {
    const cellKey = this.getCellKey(lat, lng);
    const bounds = this.getCellBounds(lat, lng);
    
    if (this.loadedCells.has(cellKey)) {
      const { timestamp, defects } = this.loadedCells.get(cellKey);
      if (Date.now() - timestamp < CONFIG.CELL_TTL) {
        console.log(`📦 Cache hit for cell ${cellKey}: ${defects?.length || 0} defects`);
        // ВАЖНО: при кэше тоже обновляем proximityService
        if (defects && defects.length > 0) {
          proximityService.updateDefectsCache(defects);
        }
        this.notify({ type: 'cell_cached', cell: cellKey, defects });
        return defects;
      }
    }
    
    this.notify({ type: 'loading_cell', cell: cellKey });
    try {
      const limit = zoom > 16 ? 300 : 500;
      const response = await defectsApi.get('/v1/defects/viewport/', {
        params: {
          min_longitude: bounds.min_longitude,
          min_latitude: bounds.min_latitude,
          max_longitude: bounds.max_longitude,
          max_latitude: bounds.max_latitude,
          limit
        },
        timeout: 10000
      });
      const data = response.data || [];
      const formattedDefects = this.formatDefects(data);
      console.log(`📡 Cell ${cellKey} loaded: ${formattedDefects.length} defects`);
      
      this.loadedCells.set(cellKey, { 
        defects: formattedDefects, 
        timestamp: Date.now(), 
        bounds 
      });
      
      // ВСЕГДА обновляем proximityService
      if (formattedDefects.length > 0) {
        proximityService.updateDefectsCache(formattedDefects);
      }
      
      this.notify({ type: 'cell_loaded', cell: cellKey, defects: formattedDefects, bounds });
      return formattedDefects;
    } catch (error) {
      console.error(`Failed to load cell ${cellKey}:`, error);
      this.notify({ type: 'error', cell: cellKey, error });
      return [];
    }
  }

  formatDefects(data) {
    if (!data || data.length === 0) return [];
    
    const formatted = data.map(d => {
      let coords = d.snapped_coordinates || d.original_coordinates;
      let isLine = false;
      let coordinates = null;
      let centerLat = null;
      let centerLon = null;
      
      if (coords && Array.isArray(coords)) {
        if (coords.length >= 2 && Array.isArray(coords[0]) && coords[0].length === 2) {
          isLine = true;
          coordinates = coords;
          centerLat = coords[0][1];
          centerLon = coords[0][0];
        } else if (coords.length === 2 && typeof coords[0] === 'number') {
          isLine = false;
          centerLat = coords[1];
          centerLon = coords[0];
        } else if (coords.length === 1 && Array.isArray(coords[0]) && coords[0].length === 2) {
          isLine = false;
          centerLat = coords[0][1];
          centerLon = coords[0][0];
        }
      }
      
      if (!centerLat || !centerLon) return null;
      
      return {
        id: d.id,
        lat: centerLat,
        lon: centerLon,
        coordinates,
        geometry_type: isLine ? 'linestring' : 'point',
        defect_type: d.defect_type,
        severity: d.severity,
        description: d.description || '',
        status: d.status,
        road_name: d.road_name,
        created_at: d.created_at,
        color: SEVERITY_COLORS[d.severity] || SEVERITY_COLORS.low
      };
    }).filter(d => d !== null);
    
    console.log(`📊 Formatted ${formatted.length} defects with valid coordinates`);
    return formatted;
  }

  async loadArea(centerLat, centerLng, zoom, force = false) {
    if (this.isLoading && !force) return;
    
    const centerCell = this.getCellKey(centerLat, centerLng);
    const cellCenter = this.getCellCenter(centerLat, centerLng);
    const distanceToCenter = this.getDistance(centerLat, centerLng, cellCenter.lat, cellCenter.lng);
    const shouldLoad = force || this.currentCenterCell !== centerCell || distanceToCenter > CONFIG.GRID_SIZE * 111000 * CONFIG.PRELOAD_THRESHOLD;
    
    if (!shouldLoad) {
      console.log(`⏭️ Skipping area load - cell ${centerCell} already loaded`);
      return null;
    }
    
    this.currentCenterCell = centerCell;
    this.currentZoom = zoom;
    this.isLoading = true;
    
    const [latCell, lngCell] = centerCell.split(',').map(Number);
    const cellsToLoad = [];
    const radius = CONFIG.LOAD_RADIUS_CELLS;
    
    for (let i = -radius; i <= radius; i++) {
      for (let j = -radius; j <= radius; j++) {
        cellsToLoad.push(`${latCell + i},${lngCell + j}`);
      }
    }
    
    console.log(`📌 Loading ${cellsToLoad.length} cells around ${centerCell}`);
    this.notify({ type: 'loading_area', cells: cellsToLoad });
    
    const loadPromises = cellsToLoad.map(cell => {
      const [lat, lng] = cell.split(',').map(Number);
      const cellLat = lat * CONFIG.GRID_SIZE + CONFIG.GRID_SIZE / 2;
      const cellLng = lng * CONFIG.GRID_SIZE + CONFIG.GRID_SIZE / 2;
      return this.loadCell(cellLat, cellLng, zoom);
    });
    
    const results = await Promise.all(loadPromises);
    const uniqueDefects = new Map();
    
    for (const defects of results) {
      if (defects) {
        for (const defect of defects) {
          if (!uniqueDefects.has(defect.id)) {
            uniqueDefects.set(defect.id, defect);
          }
        }
      }
    }
    
    const allDefects = Array.from(uniqueDefects.values());
    console.log(`📦 Area loaded: ${allDefects.length} unique defects from ${cellsToLoad.length} cells`);
    
    // Обновляем proximityService всеми дефектами области
    if (allDefects.length > 0) {
      proximityService.updateDefectsCache(allDefects);
    }
    
    this.notify({ type: 'area_loaded', defects: allDefects, cells: cellsToLoad, centerCell, zoom });
    this.isLoading = false;
    return allDefects;
  }

  async smartLoad(centerLat, centerLng, zoom, bounds = null) {
    console.log(`🎯 SmartLoad: center=${centerLat},${centerLng}, zoom=${zoom}`);
    
    if (zoom < 12 && bounds) {
      return this.loadViewport(bounds, zoom);
    } else {
      return this.loadArea(centerLat, centerLng, zoom);
    }
  }

  onUserMove(lat, lng, zoom, bounds) {
    if (this.loadTimeout) clearTimeout(this.loadTimeout);
    this.loadTimeout = setTimeout(() => {
      this.smartLoad(lat, lng, zoom, bounds);
    }, CONFIG.IDLE_DELAY);
  }

  getDistance(lat1, lng1, lat2, lng2) {
    const R = 6371000;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + 
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
              Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  clearCache() {
    this.loadedCells.clear();
    proximityService.clearCache();
    console.log('🗑️ Grid cache cleared');
  }

  getStats() {
    return { 
      loadedCells: this.loadedCells.size, 
      currentCell: this.currentCenterCell, 
      currentZoom: this.currentZoom 
    };
  }
}

export const defectsGrid = new DefectsGridManager();