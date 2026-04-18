// MobileApp/src/screens/EditDefectScreen.js
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView,
  TextInput, Alert, ActivityIndicator, Image, Platform, Animated
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Picker } from '@react-native-picker/picker';
import { updateDefect, deleteDefect, getDefectById, DEFECT_TYPES, DEFECT_TYPE_LABELS, SEVERITY_LEVELS, SEVERITY_LABELS } from '../services/defectsService';
import { useAuth } from '../context/AuthContext';
import { getPhotoUrl } from '../utils/urlHelper';

// Компонент Toast уведомлений
const Toast = ({ visible, message, type, onHide }) => {
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 1,
          duration: 300,
          useNativeDriver: Platform.OS !== 'web',
        }),
        Animated.delay(3000),
        Animated.timing(opacity, {
          toValue: 0,
          duration: 300,
          useNativeDriver: Platform.OS !== 'web',
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

export default function EditDefectScreen({ navigation, route }) {
  const { user, isVerified } = useAuth();
  const { defectId } = route.params;
  
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [toast, setToast] = useState({ visible: false, message: '', type: 'info' });
  
  const [defectType, setDefectType] = useState(DEFECT_TYPES.POTHOLE);
  const [severity, setSeverity] = useState(SEVERITY_LEVELS.MEDIUM);
  const [description, setDescription] = useState('');
  const [existingPhotos, setExistingPhotos] = useState([]);
  const [originalDefect, setOriginalDefect] = useState(null);

  const showToast = useCallback((message, type = 'info') => {
    setToast({ visible: true, message, type });
  }, []);

  // Загрузка данных дефекта
  useEffect(() => {
    fetchDefectData();
  }, [defectId]);

  const fetchDefectData = async () => {
    try {
      const defect = await getDefectById(defectId);
      setOriginalDefect(defect);
      setDefectType(defect.defect_type);
      setSeverity(defect.severity);
      setDescription(defect.description || '');
      setExistingPhotos(defect.photos || []);
    } catch (error) {
      console.error('Fetch defect error:', error);
      showToast('Не удалось загрузить данные дефекта', 'error');
      setTimeout(() => navigation.goBack(), 2000);
    } finally {
      setFetching(false);
    }
  };

  const handleUpdate = async () => {
    if (!user || !isVerified) {
      Alert.alert('Ошибка', 'У вас нет прав для редактирования');
      return;
    }

    if (!originalDefect) {
      showToast('Ошибка загрузки данных дефекта', 'error');
      return;
    }

    // Проверяем, были ли изменения
    const hasChanges = 
      defectType !== originalDefect.defect_type ||
      severity !== originalDefect.severity ||
      description !== (originalDefect.description || '');

    if (!hasChanges) {
      showToast('Нет изменений для сохранения', 'info');
      return;
    }

    setLoading(true);
    try {
      // Используем прямой update через API
      await updateDefect(defectId, {
        defect_type: defectType,
        severity: severity,
        description: description.trim()
      });

      showToast('✅ Дефект успешно обновлён!', 'success');
      
      setTimeout(() => {
        navigation.goBack();
      }, 1500);
    } catch (error) {
      console.error('Update defect error:', error);
      
      let errorMessage = 'Не удалось обновить дефект';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail.map(d => d.msg || d).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (typeof detail === 'object') {
          errorMessage = detail.detail || detail.message || JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      showToast(`❌ Ошибка: ${errorMessage}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = () => {
    Alert.alert(
      'Удаление дефекта',
      'Вы уверены, что хотите удалить этот дефект? Это действие нельзя отменить.',
      [
        { text: 'Отмена', style: 'cancel' },
        {
          text: 'Удалить',
          style: 'destructive',
          onPress: async () => {
            setLoading(true);
            try {
              await deleteDefect(defectId);
              showToast('✅ Дефект удалён', 'success');
              setTimeout(() => {
                navigation.goBack();
              }, 1500);
            } catch (error) {
              console.error('Delete error:', error);
              showToast('❌ Не удалось удалить дефект', 'error');
              setLoading(false);
            }
          }
        }
      ]
    );
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

  if (fetching) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
        <Text style={styles.loadingText}>Загрузка данных...</Text>
      </View>
    );
  }

  const hasChanges = 
    defectType !== originalDefect?.defect_type ||
    severity !== originalDefect?.severity ||
    description !== (originalDefect?.description || '');

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#0f172a" />
        </TouchableOpacity>
        <Text style={styles.title}>Редактирование дефекта</Text>
        <TouchableOpacity onPress={handleDelete} style={styles.deleteBtn}>
          <Ionicons name="trash-outline" size={24} color="#ef4444" />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
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
            placeholder="Опишите проблему..."
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
          {existingPhotos.length > 0 && (
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.photoList}>
              {existingPhotos.map((photo, index) => (
                <View key={`existing-${index}`} style={styles.photoItem}>
                  <Image source={{ uri: getPhotoUrl(photo) }} style={styles.photoImage} />
                </View>
              ))}
            </ScrollView>
          )}
          
          {existingPhotos.length === 0 && (
            <Text style={styles.photoHint}>📸 Фото отсутствуют</Text>
          )}
          
          <Text style={styles.photoNote}>
            ℹ️ Фото нельзя изменить при редактировании. Для изменения фото создайте новый дефект.
          </Text>
        </View>

        <TouchableOpacity
          style={[styles.submitBtn, (!hasChanges || loading) && styles.submitBtnDisabled]}
          onPress={handleUpdate}
          disabled={!hasChanges || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="save-outline" size={20} color="#fff" />
              <Text style={styles.submitBtnText}>Сохранить изменения</Text>
            </>
          )}
        </TouchableOpacity>
        
        <Text style={styles.noteText}>
          ℹ️ При редактировании можно изменить только тип, серьёзность и описание дефекта
        </Text>
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
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' },
  loadingText: { marginTop: 12, fontSize: 14, color: '#64748b' },
  
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
  deleteBtn: { padding: 8 },
  
  scrollContent: { padding: 16, paddingBottom: 40 },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 16, borderWidth: 1, borderColor: '#e2e8f0' },
  label: { fontSize: 14, fontWeight: '600', color: '#475569', marginBottom: 12 },
  
  pickerWrapper: { backgroundColor: '#f8fafc', borderRadius: 8, borderWidth: 1, borderColor: '#e2e8f0', overflow: 'hidden' },
  picker: { height: 50 },
  
  severityButtons: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  severityBtn: { flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: '#f1f5f9', alignItems: 'center', minWidth: 80 },
  severityBtnText: { fontSize: 13, fontWeight: '500', color: '#64748b' },
  severityBtnTextActive: { color: '#fff' },
  
  textarea: { backgroundColor: '#f8fafc', padding: 12, borderRadius: 8, borderWidth: 1, borderColor: '#e2e8f0', minHeight: 100, fontSize: 14 },
  charCount: { textAlign: 'right', fontSize: 11, color: '#94a3b8', marginTop: 4 },
  
  photoList: { flexDirection: 'row', marginTop: 8 },
  photoItem: { width: 100, height: 100, borderRadius: 8, marginRight: 8, overflow: 'hidden', backgroundColor: '#f1f5f9' },
  photoImage: { width: '100%', height: '100%' },
  photoHint: { textAlign: 'center', fontSize: 13, color: '#94a3b8', paddingVertical: 12 },
  photoNote: { textAlign: 'center', fontSize: 11, color: '#64748b', marginTop: 8, fontStyle: 'italic' },
  
  submitBtn: { backgroundColor: '#2563eb', padding: 16, borderRadius: 12, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 8, marginTop: 8 },
  submitBtnDisabled: { opacity: 0.6 },
  submitBtnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  
  noteText: { textAlign: 'center', fontSize: 12, color: '#64748b', marginTop: 16, fontStyle: 'italic' },
  
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