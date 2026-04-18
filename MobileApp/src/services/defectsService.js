// MobileApp/src/services/defectsService.js
import { Platform } from 'react-native';
import { defectsApi } from '../config/api';

export const DEFECT_TYPES = {
  LONGITUDINAL_CRACK: 'longitudinal_crack',
  TRANSVERSE_CRACK: 'transverse_crack',
  ALLIGATOR_CRACK: 'alligator_crack',
  REPAIRED_CRACK: 'repaired_crack',
  POTHOLE: 'pothole',
  CROSSWALK_BLUR: 'crosswalk_blur',
  LANE_LINE_BLUR: 'lane_line_blur',
  MANHOLE_COVER: 'manhole_cover',
  PATCH: 'patch',
  RUTTING: 'rutting',
  OTHER: 'other'
};

export const DEFECT_TYPE_LABELS = {
  [DEFECT_TYPES.LONGITUDINAL_CRACK]: 'Продольная трещина',
  [DEFECT_TYPES.TRANSVERSE_CRACK]: 'Поперечная трещина',
  [DEFECT_TYPES.ALLIGATOR_CRACK]: 'Сетка трещин',
  [DEFECT_TYPES.REPAIRED_CRACK]: 'Заделанная трещина',
  [DEFECT_TYPES.POTHOLE]: 'Яма',
  [DEFECT_TYPES.CROSSWALK_BLUR]: 'Стёртый переход',
  [DEFECT_TYPES.LANE_LINE_BLUR]: 'Стёртая разметка',
  [DEFECT_TYPES.MANHOLE_COVER]: 'Люк',
  [DEFECT_TYPES.PATCH]: 'Платка',
  [DEFECT_TYPES.RUTTING]: 'Колейность',
  [DEFECT_TYPES.OTHER]: 'Другое'
};

export const SEVERITY_LEVELS = { LOW: 'low', MEDIUM: 'medium', HIGH: 'high', CRITICAL: 'critical' };
export const SEVERITY_LABELS = { low: 'Низкий', medium: 'Средний', high: 'Высокий', critical: 'Критический' };
export const DEFECT_STATUSES = { PENDING: 'pending', APPROVED: 'approved', REJECTED: 'rejected', FIXED: 'fixed' };

export const getNearbyDefects = async ({ latitude, longitude, radius_meters = 500, defect_types, min_severity }) => {
  const { data } = await defectsApi.get('/v1/defects/nearby/', {
    params: { latitude, longitude, radius_meters, defect_types, min_severity }
  });
  return data;
};

export const getDefectsByViewport = async ({
  min_longitude,
  min_latitude,
  max_longitude,
  max_latitude,
  limit = 500,
  defect_types,
  min_severity
}) => {
  const { data } = await defectsApi.get('/v1/defects/viewport/', {
    params: {
      min_longitude,
      min_latitude,
      max_longitude,
      max_latitude,
      limit,
      defect_types,
      min_severity
    }
  });
  return data;
};

export const getPendingDefects = async ({ limit = 50, offset = 0 } = {}) => {
  const { data } = await defectsApi.get('/v1/defects/pending/', { params: { limit, offset } });
  return data;
};

export const moderateDefect = async (defect_id, { status, rejection_reason }) => {
  const formData = new URLSearchParams();
  formData.append('status', status);
  if (rejection_reason) formData.append('rejection_reason', rejection_reason);
  const { data } = await defectsApi.patch(`/v1/defects/${defect_id}/moderate`, formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  return data;
};

// Получение дефекта по ID
export const getDefectById = async (defectId) => {
  const { data } = await defectsApi.get(`/v1/defects/${defectId}`);
  return data;
};

// Удаление дефекта
export const deleteDefect = async (defectId) => {
  try {
    const { data } = await defectsApi.delete(`/v1/defects/${defectId}`);
    return data;
  } catch (error) {
    console.error('Delete defect error:', error);
    throw error;
  }
};


export const snapPoint = async ({ longitude, latitude, max_distance_meters = 15 }) => {
  const { data } = await defectsApi.post('/v1/snap-point', {
    longitude, latitude, max_distance_meters
  });
  return data;
};

export const createDefect = async ({ defect_type, severity, geometry_type, coordinates, description = '', max_distance_meters = 15, photos = [] }) => {
  const formData = new FormData();
  formData.append('defect_type', defect_type);
  formData.append('severity', severity);
  formData.append('geometry_type', geometry_type);
  formData.append('coordinates', JSON.stringify(coordinates));
  formData.append('description', description);
  formData.append('max_distance_meters', String(max_distance_meters));
  
  for (let i = 0; i < photos.length; i++) {
    const photo = photos[i];
    
    if (Platform.OS === 'web') {
      if (photo.uri && photo.uri.startsWith('data:image')) {
        const base64Data = photo.uri.split(',')[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let j = 0; j < byteCharacters.length; j++) {
          byteNumbers[j] = byteCharacters.charCodeAt(j);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: photo.type || 'image/jpeg' });
        formData.append('photos', blob, `photo_${Date.now()}_${i}.jpg`);
      } else if (photo.uri) {
        try {
          const response = await fetch(photo.uri);
          const blob = await response.blob();
          formData.append('photos', blob, `photo_${Date.now()}_${i}.jpg`);
        } catch (err) {
          console.error('Error fetching blob:', err);
        }
      }
    } else {
      const uriParts = photo.uri.split('.');
      const fileType = uriParts[uriParts.length - 1];
      
      formData.append('photos', {
        uri: photo.uri,
        name: `photo_${Date.now()}_${i}.${fileType}`,
        type: photo.type || `image/${fileType}`,
      });
    }
  }
  
  const { data } = await defectsApi.post('/v1/defects/create', formData, {
    headers: { 
      'Content-Type': 'multipart/form-data',
    },
  });
  return data;
};

export const updateDefect = async (defectId, { defect_type, severity, description }) => {
  const params = new URLSearchParams();
  if (defect_type) params.append('defect_type', defect_type);
  if (severity) params.append('severity', severity);
  if (description) params.append('description', description);
  
  const { data } = await defectsApi.patch(`/v1/defects/${defectId}/update?${params.toString()}`);
  return data;
};