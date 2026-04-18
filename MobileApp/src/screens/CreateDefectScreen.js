import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView,
  TextInput, Alert, ActivityIndicator, Image, Platform, Animated
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { Picker } from '@react-native-picker/picker';
import { createDefect, DEFECT_TYPES, DEFECT_TYPE_LABELS, SEVERITY_LEVELS, SEVERITY_LABELS, snapPoint } from '../services/defectsService';
import { useAuth } from '../context/AuthContext';

// Компонент Toast уведомлений
const Toast = ({ visible, message, type, onHide }) => {
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.delay(3000),
        Animated.timing(opacity, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start(() => onHide());
    }
  }, [visible, opacity, onHide]);

  if (!visible) return null;

  const backgroundColor = type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6';
  const icon = type === 'success' ? 'checkmark-circle' : type === 'error' ? 'alert-circle' : 'information-circle';

  return (
    <Animated.View style={[styles.toast, { backgroundColor, opacity }]}>
      <Ionicons name={icon} size={20} color="#fff" />
      <Text style={styles.toastText}>{message}</Text>
    </Animated.View>
  );
};

export default function CreateDefectScreen({ navigation, route }) {
  const { user, isVerified } = useAuth();
  const { 
    geometryType: routeGeometryType = null,
    coordinates: routeCoordinates = null,
  } = route.params || {};
  
  const [coordinates, setCoordinates] = useState(routeCoordinates || []);
  const [toast, setToast] = useState({ visible: false, message: '', type: 'info' });
  
  const getGeometryTypeFromCoords = (coords) => {
    if (!coords || coords.length === 0) return 'point';
    if (routeGeometryType) return routeGeometryType;
    if (Array.isArray(coords[0]) && coords[0].length === 2) {
      return coords.length === 1 ? 'point' : 'linestring';
    }
    return 'point';
  };
  
  const [geometryType, setGeometryType] = useState(getGeometryTypeFromCoords(coordinates));
  const [isSnapping, setIsSnapping] = useState(false);
  const [snappedInfo, setSnappedInfo] = useState(null);
  
  const [defectType, setDefectType] = useState(DEFECT_TYPES.POTHOLE);
  const [severity, setSeverity] = useState(SEVERITY_LEVELS.MEDIUM);
  const [description, setDescription] = useState('');
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(false);

  const showToast = useCallback((message, type = 'info') => {
    setToast({ visible: true, message, type });
  }, []);

  useEffect(() => {
    if (Platform.OS !== 'web') {
      (async () => {
        const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
        const { status: libraryStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (cameraStatus !== 'granted') {
          showToast('Нет доступа к камере', 'error');
        }
        if (libraryStatus !== 'granted') {
          showToast('Нет доступа к галерее', 'error');
        }
      })();
    }
  }, [showToast]);

  const normalizeCoordinates = () => {
    if (!coordinates || coordinates.length === 0) return null;
    
    if (coordinates.length === 2 && typeof coordinates[0] === 'number') {
      return [coordinates];
    }
    if (Array.isArray(coordinates[0]) && coordinates[0].length === 2) {
      return coordinates;
    }
    
    return coordinates;
  };

  useEffect(() => {
    const performSnapping = async () => {
      const normalizedCoords = normalizeCoordinates();
      if (!normalizedCoords || normalizedCoords.length === 0) return;
      
      if (geometryType === 'point' && normalizedCoords[0]) {
        const point = normalizedCoords[0];
        setIsSnapping(true);
        try {
          const snapped = await snapPoint({
            longitude: point[0],
            latitude: point[1],
            max_distance_meters: 15
          });
          
          if (snapped && snapped.snapped_longitude) {
            setSnappedInfo(snapped);
            if (snapped.distance_meters > 15) {
              showToast(`Точка далеко от дороги (${snapped.distance_meters.toFixed(0)} м)`, 'error');
            } else if (snapped.road_info?.road_name) {
              showToast(`Привязано к дороге: ${snapped.road_info.road_name}`, 'success');
            }
          }
        } catch (error) {
          console.error('Snapping error:', error);
          showToast('Ошибка привязки к дороге', 'error');
        } finally {
          setIsSnapping(false);
        }
      }
      else if (geometryType === 'linestring' && normalizedCoords.length >= 2) {
        setIsSnapping(true);
        try {
          const firstPoint = normalizedCoords[0];
          const lastPoint = normalizedCoords[normalizedCoords.length - 1];
          
          const [snappedFirst, snappedLast] = await Promise.all([
            snapPoint({ longitude: firstPoint[0], latitude: firstPoint[1], max_distance_meters: 15 }),
            snapPoint({ longitude: lastPoint[0], latitude: lastPoint[1], max_distance_meters: 15 })
          ]);
          
          setSnappedInfo({
            start: snappedFirst,
            end: snappedLast,
            road_name: snappedFirst.road_info?.road_name || snappedLast.road_info?.road_name
          });
          
          if (snappedFirst.distance_meters > 15 || snappedLast.distance_meters > 15) {
            showToast('Некоторые точки далеко от дороги', 'error');
          } else if (snappedFirst.road_info?.road_name) {
            showToast(`Линия привязана к дороге: ${snappedFirst.road_info.road_name}`, 'success');
          }
        } catch (error) {
          console.error('Snapping error:', error);
          showToast('Ошибка привязки к дороге', 'error');
        } finally {
          setIsSnapping(false);
        }
      }
    };
    
    performSnapping();
  }, [coordinates, geometryType, showToast]);

  const pickImage = async () => {
    try {
      if (Platform.OS === 'web') {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/jpeg,image/png,image/jpg';
        input.multiple = false;
        
        input.onchange = (e) => {
          const file = e.target.files[0];
          if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
              setPhotos([...photos, {
                uri: reader.result,
                type: file.type,
                name: file.name,
              }]);
              showToast('Фото добавлено', 'success');
            };
            reader.readAsDataURL(file);
          }
        };
        
        input.click();
        return;
      }
      
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'Images',
        allowsEditing: true,
        quality: 0.8,
        base64: false,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        setPhotos([...photos, {
          uri: result.assets[0].uri,
          type: 'image/jpeg',
        }]);
        showToast('Фото добавлено', 'success');
      }
    } catch (error) {
      console.error('Pick image error:', error);
      showToast('Не удалось выбрать изображение', 'error');
    }
  };

  const takePhoto = async () => {
    try {
      if (Platform.OS === 'web') {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/jpeg,image/png,image/jpg';
        input.capture = 'environment';
        input.multiple = false;
        
        input.onchange = (e) => {
          const file = e.target.files[0];
          if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
              setPhotos([...photos, {
                uri: reader.result,
                type: file.type,
                name: file.name,
              }]);
              showToast('Фото добавлено', 'success');
            };
            reader.readAsDataURL(file);
          }
        };
        
        input.click();
        return;
      }
      
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: 'Images',
        allowsEditing: true,
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        setPhotos([...photos, {
          uri: result.assets[0].uri,
          type: 'image/jpeg',
        }]);
        showToast('Фото добавлено', 'success');
      }
    } catch (error) {
      console.error('Take photo error:', error);
      showToast('Не удалось сделать фото', 'error');
    }
  };

  const removePhoto = (index) => {
    setPhotos(photos.filter((_, i) => i !== index));
    showToast('Фото удалено', 'info');
  };

  const handleSubmit = async () => {
    if (!user) {
      Alert.alert('Ошибка', 'Необходимо авторизоваться', [
        { text: 'Войти', onPress: () => navigation.navigate('Login') },
        { text: 'Отмена', style: 'cancel' }
      ]);
      return;
    }
    
    if (!isVerified) {
      Alert.alert(
        'Требуется верификация',
        'Добавлять дефекты могут только верифицированные пользователи.\nПодтвердите email в профиле.',
        [{ text: 'OK' }]
      );
      return;
    }

    const normalizedCoords = normalizeCoordinates();
    if (!normalizedCoords || normalizedCoords.length === 0) {
      showToast('Не указаны координаты дефекта', 'error');
      return;
    }

    const actualGeometryType = normalizedCoords.length === 1 ? 'point' : 'linestring';
    
    if (actualGeometryType === 'linestring' && normalizedCoords.length < 2) {
      showToast('Для линейного дефекта нужно минимум 2 точки', 'error');
      return;
    }

    if (photos.length === 0) {
      showToast('Добавьте хотя бы одно фото дефекта', 'error');
      return;
    }

    setLoading(true);
    try {
      const coordinatesToSend = normalizedCoords;
      
      const result = await createDefect({
        defect_type: defectType,
        severity: severity,
        geometry_type: actualGeometryType,
        coordinates: coordinatesToSend,
        description: description.trim(),
        photos: photos,
        max_distance_meters: 15
      });

      if (result && result.id) {
        showToast('✅ Дефект успешно создан и отправлен на модерацию!', 'success');
        
        setTimeout(() => {
          navigation.goBack();
        }, 2000);
      } else {
        throw new Error('Не получен ответ от сервера');
      }
    } catch (error) {
      console.error('Create defect error:', error);
      
      let errorMessage = 'Не удалось создать дефект';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail.map(d => d.msg || d).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      showToast(`❌ Ошибка: ${errorMessage}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const defectTypeOptions = Object.entries(DEFECT_TYPES).map(([key, value]) => ({
    label: DEFECT_TYPE_LABELS[value],
    value: value,
  }));

  const severityOptions = Object.entries(SEVERITY_LEVELS).map(([key, value]) => ({
    label: SEVERITY_LABELS[value],
    value: value,
  }));

  const getSeverityColor = () => {
    switch (severity) {
      case SEVERITY_LEVELS.CRITICAL: return '#dc2626';
      case SEVERITY_LEVELS.HIGH: return '#f97316';
      case SEVERITY_LEVELS.MEDIUM: return '#f59e0b';
      default: return '#22c55e';
    }
  };

  const formatCoordinates = () => {
    const normalizedCoords = normalizeCoordinates();
    if (!normalizedCoords || normalizedCoords.length === 0) return 'Не выбраны';
    
    if (geometryType === 'point' && normalizedCoords[0]) {
      const point = normalizedCoords[0];
      return `${point[1].toFixed(6)}°, ${point[0].toFixed(6)}°`;
    } else if (normalizedCoords.length >= 2) {
      const firstPoint = normalizedCoords[0];
      const lastPoint = normalizedCoords[normalizedCoords.length - 1];
      return `${normalizedCoords.length} точек: от (${firstPoint[1].toFixed(4)}°, ${firstPoint[0].toFixed(4)}°) до (${lastPoint[1].toFixed(4)}°, ${lastPoint[0].toFixed(4)}°)`;
    }
    return `${normalizedCoords.length} координат`;
  };

  const normalizedCoords = normalizeCoordinates();
  const pointCount = normalizedCoords?.length || 0;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#0f172a" />
        </TouchableOpacity>
        <Text style={styles.title}>Создание дефекта</Text>
        <TouchableOpacity onPress={handleSubmit} disabled={loading} style={styles.submitHeaderBtn}>
          {loading ? (
            <ActivityIndicator size="small" color="#2563eb" />
          ) : (
            <Ionicons name="send" size={24} color="#2563eb" />
          )}
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <View style={styles.card}>
          <Text style={styles.label}>Тип дефекта</Text>
          <View style={styles.geometryBadge}>
            <Ionicons 
              name={pointCount === 1 ? "location-outline" : "barcode-outline"} 
              size={20} 
              color={pointCount === 1 ? '#f59e0b' : '#10b981'} 
            />
            <Text style={styles.geometryText}>
              {pointCount === 1 ? 'Точечный дефект' : 'Линейный дефект'}
            </Text>
            <Text style={styles.geometryHint}>
              ({pointCount === 1 ? '1 точка' : `${pointCount} точек`})
            </Text>
          </View>
          <Text style={styles.geometryNote}>
            {pointCount === 1 
              ? '📍 Дефект в одной точке (яма, люк, трещина)' 
              : '📏 Протяжённый дефект (колея, длинная трещина)'}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>Местоположение</Text>
          {isSnapping ? (
            <View style={styles.snappingContainer}>
              <ActivityIndicator size="small" color="#2563eb" />
              <Text style={styles.snappingText}>Привязка к дороге...</Text>
            </View>
          ) : (
            <>
              <View style={styles.coordRow}>
                <Ionicons name="location-outline" size={20} color="#64748b" />
                <Text style={styles.coordText}>{formatCoordinates()}</Text>
              </View>
              {snappedInfo && (snappedInfo.road_name || snappedInfo.road_info?.road_name) && (
                <View style={styles.roadInfo}>
                  <Ionicons name="map-outline" size={16} color="#10b981" />
                  <Text style={styles.roadText}>
                    Дорога: {snappedInfo.road_name || snappedInfo.road_info?.road_name}
                  </Text>
                </View>
              )}
              {snappedInfo?.distance_meters !== undefined && (
                <Text style={[styles.distanceText, snappedInfo.distance_meters > 15 && styles.distanceTextError]}>
                  Расстояние до дороги: {snappedInfo.distance_meters.toFixed(1)} м
                  {snappedInfo.distance_meters > 15 && ' (слишком далеко)'}
                </Text>
              )}
            </>
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>Вид дефекта</Text>
          <View style={styles.pickerWrapper}>
            <Picker
              selectedValue={defectType}
              onValueChange={setDefectType}
              style={styles.picker}
              dropdownIconColor="#64748b"
            >
              {defectTypeOptions.map(opt => (
                <Picker.Item key={opt.value} label={opt.label} value={opt.value} />
              ))}
            </Picker>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>Серьёзность</Text>
          <View style={styles.severityButtons}>
            {severityOptions.map(opt => (
              <TouchableOpacity
                key={opt.value}
                style={[
                  styles.severityBtn,
                  severity === opt.value && { backgroundColor: getSeverityColor() }
                ]}
                onPress={() => setSeverity(opt.value)}
              >
                <Text style={[
                  styles.severityBtnText,
                  severity === opt.value && styles.severityBtnTextActive
                ]}>
                  {opt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>Описание</Text>
          <TextInput
            style={styles.textarea}
            placeholder="Опишите проблему (необязательно)..."
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
            maxLength={500}
          />
          <Text style={styles.charCount}>{description.length}/500</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>Фотографии</Text>
          <View style={styles.photoActions}>
            <TouchableOpacity style={[styles.photoBtn, styles.cameraBtn]} onPress={takePhoto}>
              <Ionicons name="camera-outline" size={20} color="#fff" />
              <Text style={styles.photoBtnText}>Снять фото</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.photoBtn, styles.galleryBtn]} onPress={pickImage}>
              <Ionicons name="images-outline" size={20} color="#fff" />
              <Text style={styles.photoBtnText}>Из галереи</Text>
            </TouchableOpacity>
          </View>

          {photos.length > 0 && (
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.photoList}>
              {photos.map((photo, index) => (
                <View key={index} style={styles.photoItem}>
                  <Image source={{ uri: photo.uri }} style={styles.photoImage} />
                  <TouchableOpacity
                    style={styles.removePhotoBtn}
                    onPress={() => removePhoto(index)}
                  >
                    <Ionicons name="close-circle" size={24} color="#ef4444" />
                  </TouchableOpacity>
                </View>
              ))}
            </ScrollView>
          )}
          
          {photos.length === 0 && (
            <Text style={styles.photoHint}>📸 Добавьте фото дефекта (обязательно)</Text>
          )}
        </View>

        <TouchableOpacity
          style={[styles.submitBtn, loading && styles.submitBtnDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="send-outline" size={20} color="#fff" />
              <Text style={styles.submitBtnText}>Отправить на модерацию</Text>
            </>
          )}
        </TouchableOpacity>

        <View style={styles.infoBox}>
          <Ionicons name="information-circle-outline" size={20} color="#64748b" />
          <Text style={styles.infoText}>
            Дефект будет проверен модератором перед публикацией на карте
          </Text>
        </View>
      </ScrollView>

      <Toast 
        visible={toast.visible} 
        message={toast.message} 
        type={toast.type} 
        onHide={() => setToast(prev => ({ ...prev, visible: false }))} 
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  header: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between',
    padding: 20, 
    paddingBottom: 10, 
    backgroundColor: '#fff', 
    borderBottomWidth: 1, 
    borderBottomColor: '#e2e8f0' 
  },
  backBtn: { padding: 8, marginRight: 12, borderRadius: 8, backgroundColor: '#f8fafc', borderWidth: 1, borderColor: '#e2e8f0' },
  title: { fontSize: 20, fontWeight: '700', color: '#0f172a', flex: 1 },
  submitHeaderBtn: { padding: 8 },
  
  scrollContent: { padding: 16, paddingBottom: 40 },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 16, borderWidth: 1, borderColor: '#e2e8f0' },
  label: { fontSize: 14, fontWeight: '600', color: '#475569', marginBottom: 12 },
  
  geometryBadge: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 8, flexWrap: 'wrap' },
  geometryText: { fontSize: 15, fontWeight: '500', color: '#0f172a' },
  geometryHint: { fontSize: 12, color: '#94a3b8' },
  geometryNote: { fontSize: 12, color: '#64748b', marginTop: 8, fontStyle: 'italic' },
  
  coordRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  coordText: { fontSize: 13, color: '#64748b', fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', flex: 1 },
  roadInfo: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#f1f5f9' },
  roadText: { fontSize: 13, color: '#10b981', flex: 1 },
  distanceText: { fontSize: 12, color: '#94a3b8', marginTop: 4 },
  distanceTextError: { color: '#ef4444' },
  snappingContainer: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 8 },
  snappingText: { fontSize: 13, color: '#64748b' },
  
  pickerWrapper: { backgroundColor: '#f8fafc', borderRadius: 8, borderWidth: 1, borderColor: '#e2e8f0', overflow: 'hidden' },
  picker: { height: 50 },
  
  severityButtons: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  severityBtn: { flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: '#f1f5f9', alignItems: 'center', minWidth: 80 },
  severityBtnText: { fontSize: 13, fontWeight: '500', color: '#64748b' },
  severityBtnTextActive: { color: '#fff' },
  
  textarea: { backgroundColor: '#f8fafc', padding: 12, borderRadius: 8, borderWidth: 1, borderColor: '#e2e8f0', minHeight: 100, fontSize: 14 },
  charCount: { textAlign: 'right', fontSize: 11, color: '#94a3b8', marginTop: 4 },
  
  photoActions: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  photoBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 12, borderRadius: 8, gap: 8 },
  cameraBtn: { backgroundColor: '#2563eb' },
  galleryBtn: { backgroundColor: '#10b981' },
  photoBtnText: { color: '#fff', fontSize: 14, fontWeight: '600' },
  photoList: { flexDirection: 'row' },
  photoItem: { width: 100, height: 100, borderRadius: 8, marginRight: 8, overflow: 'hidden', position: 'relative' },
  photoImage: { width: '100%', height: '100%' },
  removePhotoBtn: { position: 'absolute', top: -8, right: -8, backgroundColor: '#fff', borderRadius: 12 },
  photoHint: { textAlign: 'center', fontSize: 13, color: '#94a3b8', paddingVertical: 12 },
  
  submitBtn: { backgroundColor: '#2563eb', padding: 16, borderRadius: 12, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 8, marginTop: 8 },
  submitBtnDisabled: { opacity: 0.6 },
  submitBtnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  
  infoBox: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: 12, backgroundColor: '#f1f5f9', borderRadius: 8, marginTop: 16 },
  infoText: { flex: 1, fontSize: 12, color: '#64748b', lineHeight: 16 },
  
  toast: {
    position: 'absolute',
    bottom: 100,
    left: 20,
    right: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 12,
    gap: 8,
    zIndex: 200,
    elevation: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  toastText: { color: '#fff', fontSize: 14, fontWeight: '500', flex: 1, textAlign: 'center' },
});