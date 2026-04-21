// MobileApp/src/services/proximityService.js
import * as Notifications from 'expo-notifications';
import { Platform, Vibration } from 'react-native';
import { DEFECT_TYPE_LABELS } from './defectsService';

const CONFIG = {
  NOTIFICATION_COOLDOWN: 60 * 1000,
  GRID_CELL_SIZE: 0.01,
  CHECK_INTERVAL: 3,
  BASE_RADIUS: 80,
  MAX_RADIUS: 300,
  MIN_RADIUS: 50,
  SPEED_FACTOR: 1.5,
  CONE_ANGLE: 45,
  MIN_SPEED_FOR_DIRECTION: 5,
};

const notifiedDefects = new Map();

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

class ProximityService {
  constructor() {
    this.defectsGrid = new Map();
    this.allDefects = [];
    this.lastPosition = null;
    this.previousPosition = null;
    this.currentSpeed = 0;
    this.currentDirection = null;
    this.isMonitoring = false;
    this.checkInterval = null;
    this.onNotificationCallback = null;
    this.enabled = true;
    this.gridSize = CONFIG.GRID_CELL_SIZE;
    this.severityFilter = {
      critical: true,
      high: true,
      medium: true,
      low: true,
    };
  }

  async init() {
    try {
      const { status } = await Notifications.requestPermissionsAsync();
      if (status !== 'granted') {
        return false;
      }
      
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('defects', {
          name: 'Дефекты дорог',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 500, 200, 500],
          lightColor: '#ff231f7c',
          sound: true,
          bypassDnd: true,
        });
      }
      
      return true;
    } catch (error) {
      console.log('Notification init error:', error);
      return false;
    }
  }

  calculateDirection(fromLat, fromLng, toLat, toLng) {
    const dLng = toLng - fromLng;
    const y = Math.sin(dLng) * Math.cos(toLat);
    const x = Math.cos(fromLat) * Math.sin(toLat) -
              Math.sin(fromLat) * Math.cos(toLat) * Math.cos(dLng);
    let bearing = Math.atan2(y, x) * 180 / Math.PI;
    bearing = (bearing + 360) % 360;
    return bearing;
  }

  isInCone(defectLat, defectLng, userLat, userLng, direction, angleDegrees) {
    if (direction === null) return true;
    
    const dLng = defectLng - userLng;
    const y = Math.sin(dLng) * Math.cos(defectLat);
    const x = Math.cos(userLat) * Math.sin(defectLat) -
              Math.sin(userLat) * Math.cos(defectLat) * Math.cos(dLng);
    let angleToDefect = Math.atan2(y, x) * 180 / Math.PI;
    angleToDefect = (angleToDefect + 360) % 360;
    
    let angleDiff = Math.abs(angleToDefect - direction);
    angleDiff = Math.min(angleDiff, 360 - angleDiff);
    
    return angleDiff <= angleDegrees;
  }

  getNotificationDistance(speedKmh) {
    let distance = CONFIG.BASE_RADIUS + (speedKmh * CONFIG.SPEED_FACTOR);
    distance = Math.max(CONFIG.MIN_RADIUS, Math.min(CONFIG.MAX_RADIUS, distance));
    return Math.round(distance);
  }

  getTimeToDefect(distance, speedKmh) {
    if (speedKmh < 1) return null;
    const seconds = (distance / 1000) / (speedKmh / 3600);
    return Math.round(seconds);
  }

  buildGridIndex(defects) {
    const newGrid = new Map();
    
    defects.forEach(defect => {
      if (!defect.lat || !defect.lon) return;
      
      const cellKey = this.getCellKey(defect.lat, defect.lon);
      if (!newGrid.has(cellKey)) {
        newGrid.set(cellKey, []);
      }
      newGrid.get(cellKey).push(defect);
    });
    
    this.defectsGrid = newGrid;
    this.allDefects = defects;
  }

  getCellKey(lat, lng) {
    const latCell = Math.floor(lat / this.gridSize);
    const lngCell = Math.floor(lng / this.gridSize);
    return `${latCell},${lngCell}`;
  }

  getNearbyCells(lat, lng, radius) {
    const radiusCells = Math.ceil(radius / 111000 / this.gridSize) + 1;
    const centerLatCell = Math.floor(lat / this.gridSize);
    const centerLngCell = Math.floor(lng / this.gridSize);
    const cells = [];
    
    for (let i = -radiusCells; i <= radiusCells; i++) {
      for (let j = -radiusCells; j <= radiusCells; j++) {
        cells.push(`${centerLatCell + i},${centerLngCell + j}`);
      }
    }
    return cells;
  }

  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  shouldNotify(defect, distance, speed) {
    if (!this.severityFilter[defect.severity]) return false;
    
    const lastNotify = notifiedDefects.get(defect.id);
    if (lastNotify && (Date.now() - lastNotify) < CONFIG.NOTIFICATION_COOLDOWN) {
      return false;
    }
    
    const notificationDistance = this.getNotificationDistance(speed);
    const inRange = distance <= notificationDistance;
    
    if (!inRange) return false;
    
    let inCone = true;
    if (speed >= CONFIG.MIN_SPEED_FOR_DIRECTION && this.currentDirection !== null) {
      inCone = this.isInCone(
        defect.lat, defect.lon,
        this.lastPosition.lat, this.lastPosition.lng,
        this.currentDirection,
        CONFIG.CONE_ANGLE
      );
    }
    
    return inRange && inCone;
  }

  async showNotification(defect, distance, timeToDefect) {
    const severityIcons = {
      critical: '⚠️ КРИТИЧЕСКИ ОПАСНО!',
      high: '🔴 Высокая опасность',
      medium: '🟡 Средняя опасность',
      low: '🟢 Низкая опасность',
    };
    
    const defectName = DEFECT_TYPE_LABELS[defect.defect_type] || defect.defect_type;
    const title = severityIcons[defect.severity] || 'Дефект';
    const body = `${defectName}\n${Math.round(distance)} м, ${timeToDefect} сек\n${defect.road_name || ''}`;
    
    try {
      const vibrationPattern = defect.severity === 'critical' ? [0, 600, 200, 600] :
                              defect.severity === 'high' ? [0, 400, 200, 400] :
                              defect.severity === 'medium' ? [0, 300] : [0, 200];
      Vibration.vibrate(vibrationPattern);
    } catch (error) {
      // Игнорируем ошибки вибрации
    }
    
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data: { defectId: defect.id, lat: defect.lat, lng: defect.lon },
          sound: true,
          priority: Notifications.AndroidNotificationPriority.HIGH,
          channelId: 'defects',
        },
        trigger: null,
      });
    } catch (error) {
      console.log('Notification error:', error);
    }
    
    notifiedDefects.set(defect.id, Date.now());
    
    if (this.onNotificationCallback) {
      this.onNotificationCallback({ defect, distance, timeToDefect });
    }
    
    return { defect, distance, timeToDefect };
  }

  getNearbyDefects(lat, lng, radius) {
    const nearbyCells = this.getNearbyCells(lat, lng, radius);
    const nearbyDefects = [];
    
    for (const cell of nearbyCells) {
      const defectsInCell = this.defectsGrid.get(cell) || [];
      for (const defect of defectsInCell) {
        const distance = this.calculateDistance(lat, lng, defect.lat, defect.lon);
        if (distance <= radius) {
          nearbyDefects.push({ ...defect, distance });
        }
      }
    }
    
    return nearbyDefects.sort((a, b) => a.distance - b.distance);
  }

  async checkNearbyDefects() {
    if (!this.enabled || !this.lastPosition) {
      return [];
    }
    
    const notificationDistance = this.getNotificationDistance(this.currentSpeed);
    const nearbyDefects = this.getNearbyDefects(
      this.lastPosition.lat,
      this.lastPosition.lng,
      notificationDistance + 100
    );
    
    const notifications = [];
    
    for (const defect of nearbyDefects) {
      if (this.shouldNotify(defect, defect.distance, this.currentSpeed)) {
        const timeToDefect = this.getTimeToDefect(defect.distance, this.currentSpeed);
        const notification = await this.showNotification(defect, defect.distance, timeToDefect);
        notifications.push(notification);
      }
    }
    
    return notifications;
  }

  updatePosition(position, speed) {
    if (this.lastPosition && speed >= CONFIG.MIN_SPEED_FOR_DIRECTION) {
      this.currentDirection = this.calculateDirection(
        this.lastPosition.lat, this.lastPosition.lng,
        position.lat, position.lng
      );
    } else if (speed < CONFIG.MIN_SPEED_FOR_DIRECTION) {
      this.currentDirection = null;
    }
    
    this.lastPosition = position;
    this.currentSpeed = speed;
  }

  startMonitoring(onNotification) {
    if (this.checkInterval) {
      this.stopMonitoring();
    }
    
    this.onNotificationCallback = onNotification;
    this.isMonitoring = true;
    
    this.checkInterval = setInterval(async () => {
      try {
        await this.checkNearbyDefects();
      } catch (error) {
        // Игнорируем ошибки
      }
    }, CONFIG.CHECK_INTERVAL * 1000);
  }

  stopMonitoring() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
    this.isMonitoring = false;
  }

  updateDefectsCache(defects) {
    if (defects && defects.length > 0) {
      this.buildGridIndex(defects);
    }
  }

  clearCache() {
    this.defectsGrid.clear();
    this.allDefects = [];
    notifiedDefects.clear();
  }

  setEnabled(enabled) {
    this.enabled = enabled;
    if (!enabled) {
      this.stopMonitoring();
    } else if (this.isMonitoring) {
      this.startMonitoring(this.onNotificationCallback);
    }
  }

  setSeverityFilter(filters) {
    this.severityFilter = { ...this.severityFilter, ...filters };
  }

  getStats() {
    return {
      enabled: this.enabled,
      isMonitoring: this.isMonitoring,
      currentSpeed: this.currentSpeed,
      currentDirection: this.currentDirection,
      totalDefects: this.allDefects.length,
      gridCells: this.defectsGrid.size,
      notifiedCount: notifiedDefects.size,
      severityFilter: { ...this.severityFilter },
    };
  }
}

export const proximityService = new ProximityService();