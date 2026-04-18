// MobileApp/src/screens/MyDefectsScreen.js
import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, FlatList,
  ActivityIndicator, RefreshControl, Image, Alert, Modal,
  ScrollView, Platform, Dimensions
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { defectsApi } from '../config/api';
import { DEFECT_TYPE_LABELS, SEVERITY_LABELS, DEFECT_STATUSES, deleteDefect } from '../services/defectsService';
import { formatDate } from '../utils/date';
import { getPhotoUrl } from '../utils/urlHelper';
import PhotoViewerModal from './PhotoViewerModal';

const { width } = Dimensions.get('window');

// Вспомогательные функции
const getStatusBadge = (status) => {
  switch (status) {
    case DEFECT_STATUSES.PENDING:
      return { text: 'На модерации', color: '#f59e0b', bg: '#fffbeb', icon: 'time-outline' };
    case DEFECT_STATUSES.APPROVED:
      return { text: 'Подтверждён', color: '#16a34a', bg: '#f0fdf4', icon: 'checkmark-circle-outline' };
    case DEFECT_STATUSES.REJECTED:
      return { text: 'Отклонён', color: '#dc2626', bg: '#fef2f2', icon: 'close-circle-outline' };
    case DEFECT_STATUSES.FIXED:
      return { text: 'Исправлен', color: '#3b82f6', bg: '#eff6ff', icon: 'construct-outline' };
    default:
      return { text: status, color: '#64748b', bg: '#f1f5f9', icon: 'help-circle-outline' };
  }
};

const getSeverityColor = (severity) => {
  switch (severity) {
    case 'critical': return '#dc2626';
    case 'high': return '#f97316';
    case 'medium': return '#f59e0b';
    default: return '#22c55e';
  }
};

const getSeverityIcon = (severity) => {
  switch (severity) {
    case 'critical': return 'alert-circle';
    case 'high': return 'warning';
    case 'medium': return 'alert';
    default: return 'information-circle';
  }
};

// Компонент карточки дефекта
const DefectCard = React.memo(({ defect, onPress, onEdit, onDelete, onPhotoPress }) => {
  const statusBadge = getStatusBadge(defect.status);
  const severityColor = getSeverityColor(defect.severity);
  const severityIcon = getSeverityIcon(defect.severity);
  const firstPhoto = defect.photos?.[0];
  const isPending = defect.status === DEFECT_STATUSES.PENDING;
  
  return (
    <TouchableOpacity
      style={styles.defectCard}
      onPress={() => onPress(defect)}
      activeOpacity={0.7}
    >
      <View style={styles.cardContent}>
        <View style={styles.defectHeader}>
          <View style={styles.defectTypeContainer}>
            <Text style={styles.defectType} numberOfLines={1}>
              {DEFECT_TYPE_LABELS[defect.defect_type] || defect.defect_type}
            </Text>
            <View style={[styles.severityBadge, { backgroundColor: `${severityColor}20` }]}>
              <Ionicons name={severityIcon} size={10} color={severityColor} />
              <Text style={[styles.severityText, { color: severityColor }]}>
                {SEVERITY_LABELS[defect.severity]}
              </Text>
            </View>
          </View>
        </View>

        {defect.description && (
          <Text style={styles.defectDescription} numberOfLines={2}>
            {defect.description}
          </Text>
        )}

        <View style={styles.defectMeta}>
          <View style={styles.metaItem}>
            <Ionicons name="location-outline" size={12} color="#94a3b8" />
            <Text style={styles.metaText} numberOfLines={1}>
              {defect.road_info?.road_name || 'Дорога не определена'}
            </Text>
          </View>
          <View style={styles.metaItem}>
            <Ionicons name="time-outline" size={12} color="#94a3b8" />
            <Text style={styles.metaText}>{formatDate(defect.created_at)}</Text>
          </View>
        </View>

        {/* Фото миниатюра */}
        {firstPhoto && (
          <TouchableOpacity 
            style={styles.thumbnailContainer}
            onPress={(e) => {
              e.stopPropagation();
              onPhotoPress(defect.photos, 0);
            }}
          >
            <Image source={{ uri: getPhotoUrl(firstPhoto) }} style={styles.thumbnail} />
            {defect.photos.length > 1 && (
              <View style={styles.thumbnailBadge}>
                <Ionicons name="images-outline" size={10} color="#fff" />
                <Text style={styles.thumbnailBadgeText}>{defect.photos.length}</Text>
              </View>
            )}
          </TouchableOpacity>
        )}
      </View>
      
      {/* Кнопки действий - вынесены в отдельный контейнер справа */}
      <View style={styles.cardActions}>
        <TouchableOpacity 
          style={styles.mapButton}
          onPress={(e) => {
            e.stopPropagation();
            onPress(defect);
          }}
        >
          <Ionicons name="map-outline" size={18} color="#2563eb" />
        </TouchableOpacity>
        {isPending && (
          <>
            <TouchableOpacity 
              style={styles.editButton}
              onPress={(e) => {
                e.stopPropagation();
                onEdit(defect);
              }}
            >
              <Ionicons name="create-outline" size={18} color="#2563eb" />
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.deleteButton}
              onPress={(e) => {
                e.stopPropagation();
                onDelete(defect);
              }}
            >
              <Ionicons name="trash-outline" size={18} color="#ef4444" />
            </TouchableOpacity>
          </>
        )}
      </View>
    </TouchableOpacity>
  );
});

// Компонент пустого состояния
const EmptyState = ({ onNavigateToMap }) => (
  <View style={styles.emptyState}>
    <View style={styles.emptyIconContainer}>
      <Ionicons name="checkmark-done-circle" size={64} color="#22c55e" />
    </View>
    <Text style={styles.emptyTitle}>У вас пока нет дефектов</Text>
    <Text style={styles.emptyText}>
      Добавьте дефект на карте, чтобы начать отслеживание
    </Text>
    <TouchableOpacity style={styles.createBtn} onPress={onNavigateToMap}>
      <Ionicons name="add-circle" size={20} color="#fff" />
      <Text style={styles.createBtnText}>Добавить дефект</Text>
    </TouchableOpacity>
  </View>
);

export default function MyDefectsScreen({ navigation }) {
  const { user, isAuthenticated } = useAuth();
  const [defects, setDefects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedDefect, setSelectedDefect] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [filter, setFilter] = useState('all');
  const [photoViewerVisible, setPhotoViewerVisible] = useState(false);
  const [photoViewerPhotos, setPhotoViewerPhotos] = useState([]);
  const [photoViewerIndex, setPhotoViewerIndex] = useState(0);

  const fetchMyDefects = useCallback(async () => {
    if (!isAuthenticated || !user) {
      setLoading(false);
      return;
    }
    
    try {
      const response = await defectsApi.get(`/v1/users/${user.oid}/defects`, {
        params: { limit: 100, offset: 0 }
      });
      
      const data = response.data;
      setDefects(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Fetch defects error:', error);
      setDefects([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    fetchMyDefects();
  }, [fetchMyDefects]);

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      fetchMyDefects();
    });
    return unsubscribe;
  }, [navigation, fetchMyDefects]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchMyDefects();
  };

  const handleDefectPress = (defect) => {
    // Получаем координаты дефекта
    const coords = defect.snapped_coordinates || defect.original_coordinates;
    if (coords && coords[0]) {
      // Передаём параметр для центрирования карты
      navigation.navigate('Map', { 
        centerTo: { 
          lat: coords[0][1], 
          lng: coords[0][0] 
        },
        zoom: 18,
        disableLocationTracking: true  // Отключаем автоматическое следование за геолокацией
      });
    } else {
      Alert.alert('Ошибка', 'Не удалось определить координаты дефекта');
    }
  };

  const handleEditDefect = (defect) => {
    navigation.navigate('EditDefect', { defectId: defect.id });
  };

  const handleDefectDelete = async (defect) => {
    Alert.alert(
      'Удаление дефекта',
      `Вы уверены, что хотите удалить дефект "${DEFECT_TYPE_LABELS[defect.defect_type] || defect.defect_type}"?`,
      [
        { text: 'Отмена', style: 'cancel' },
        {
          text: 'Удалить',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteDefect(defect.id);
              Alert.alert('Успешно', 'Дефект удалён');
              fetchMyDefects();
            } catch (error) {
              console.error('Delete error:', error);
              Alert.alert('Ошибка', 'Не удалось удалить дефект');
            }
          }
        }
      ]
    );
  };

  const handlePhotoPress = (photos, index) => {
    setPhotoViewerPhotos(photos);
    setPhotoViewerIndex(index);
    setPhotoViewerVisible(true);
  };

  const navigateToMap = () => {
    navigation.navigate('Map');
  };

  const filteredDefects = defects.filter(defect => {
    if (filter === 'all') return true;
    return defect.status === filter;
  });

  const stats = {
    total: defects.length,
    pending: defects.filter(d => d.status === DEFECT_STATUSES.PENDING).length,
    approved: defects.filter(d => d.status === DEFECT_STATUSES.APPROVED).length,
    rejected: defects.filter(d => d.status === DEFECT_STATUSES.REJECTED).length,
  };

  const renderItem = useCallback(({ item }) => (
    <DefectCard 
      defect={item} 
      onPress={handleDefectPress}
      onEdit={handleEditDefect}
      onDelete={handleDefectDelete}
      onPhotoPress={handlePhotoPress}
    />
  ), []);

  const keyExtractor = useCallback((item) => item.id, []);

  if (!isAuthenticated) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={24} color="#0f172a" />
          </TouchableOpacity>
          <Text style={styles.title}>Мои дефекты</Text>
        </View>
        <View style={styles.notAuthContainer}>
          <Ionicons name="lock-closed" size={64} color="#94a3b8" />
          <Text style={styles.notAuthTitle}>Не авторизованы</Text>
          <Text style={styles.notAuthText}>
            Войдите в аккаунт, чтобы увидеть свои дефекты
          </Text>
          <TouchableOpacity style={styles.loginBtn} onPress={() => navigation.navigate('Login')}>
            <Text style={styles.loginBtnText}>Войти</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={24} color="#0f172a" />
          </TouchableOpacity>
          <Text style={styles.title}>Мои дефекты</Text>
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563eb" />
          <Text style={styles.loadingText}>Загрузка дефектов...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#0f172a" />
        </TouchableOpacity>
        <Text style={styles.title}>Мои дефекты</Text>
        {defects.length > 0 && (
          <View style={styles.countContainer}>
            <Text style={styles.countText}>{defects.length}</Text>
          </View>
        )}
      </View>

      {defects.length > 0 && (
        <View style={styles.statsContainer}>
          <TouchableOpacity 
            style={[styles.statItem, filter === 'all' && styles.statItemActive]} 
            onPress={() => setFilter('all')}
          >
            <Text style={[styles.statNumber, filter === 'all' && styles.statNumberActive]}>{stats.total}</Text>
            <Text style={[styles.statLabel, filter === 'all' && styles.statLabelActive]}>Всего</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.statItem, filter === 'pending' && styles.statItemActive]} 
            onPress={() => setFilter('pending')}
          >
            <Text style={[styles.statNumber, filter === 'pending' && styles.statNumberActive, { color: '#f59e0b' }]}>{stats.pending}</Text>
            <Text style={[styles.statLabel, filter === 'pending' && styles.statLabelActive]}>На проверке</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.statItem, filter === 'approved' && styles.statItemActive]} 
            onPress={() => setFilter('approved')}
          >
            <Text style={[styles.statNumber, filter === 'approved' && styles.statNumberActive, { color: '#16a34a' }]}>{stats.approved}</Text>
            <Text style={[styles.statLabel, filter === 'approved' && styles.statLabelActive]}>Подтверждены</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.statItem, filter === 'rejected' && styles.statItemActive]} 
            onPress={() => setFilter('rejected')}
          >
            <Text style={[styles.statNumber, filter === 'rejected' && styles.statNumberActive, { color: '#dc2626' }]}>{stats.rejected}</Text>
            <Text style={[styles.statLabel, filter === 'rejected' && styles.statLabelActive]}>Отклонены</Text>
          </TouchableOpacity>
        </View>
      )}

      <FlatList
        data={filteredDefects}
        renderItem={renderItem}
        keyExtractor={keyExtractor}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={<EmptyState onNavigateToMap={navigateToMap} />}
        initialNumToRender={10}
        maxToRenderPerBatch={10}
        windowSize={5}
        removeClippedSubviews={Platform.OS !== 'web'}
        showsVerticalScrollIndicator={false}
      />

      <PhotoViewerModal
        visible={photoViewerVisible}
        photos={photoViewerPhotos}
        initialIndex={photoViewerIndex}
        onClose={() => setPhotoViewerVisible(false)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  
  header: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: 16, 
    backgroundColor: '#fff', 
    borderBottomWidth: 1, 
    borderBottomColor: '#e2e8f0' 
  },
  backBtn: { 
    padding: 8, 
    marginRight: 12, 
    borderRadius: 8, 
    backgroundColor: '#f8fafc', 
    borderWidth: 1, 
    borderColor: '#e2e8f0' 
  },
  title: { fontSize: 20, fontWeight: '700', color: '#0f172a', flex: 1 },
  countContainer: { 
    backgroundColor: '#eff6ff', 
    paddingHorizontal: 10, 
    paddingVertical: 4, 
    borderRadius: 12 
  },
  countText: { fontSize: 14, fontWeight: '600', color: '#2563eb' },
  
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
    gap: 8,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
    borderRadius: 10,
    backgroundColor: '#f8fafc',
  },
  statItemActive: {
    backgroundColor: '#eff6ff',
  },
  statNumber: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0f172a',
  },
  statNumberActive: {
    color: '#2563eb',
  },
  statLabel: {
    fontSize: 11,
    color: '#64748b',
    marginTop: 2,
  },
  statLabelActive: {
    color: '#2563eb',
    fontWeight: '500',
  },
  
  listContent: { padding: 16, paddingBottom: 40, flexGrow: 1 },
  
  defectCard: { 
    backgroundColor: '#fff', 
    borderRadius: 12, 
    borderWidth: 1, 
    borderColor: '#e2e8f0', 
    marginBottom: 12,
    padding: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  cardContent: {
    flex: 1,
    marginRight: 12,
  },
  defectHeader: { 
    marginBottom: 8,
  },
  defectTypeContainer: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 6, 
    flexWrap: 'wrap',
  },
  defectType: { 
    fontSize: 14, 
    fontWeight: '600', 
    color: '#0f172a',
  },
  severityBadge: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 3,
    paddingHorizontal: 6, 
    paddingVertical: 2, 
    borderRadius: 8,
  },
  severityText: { 
    fontSize: 10, 
    fontWeight: '600' 
  },
  defectDescription: { 
    fontSize: 12, 
    color: '#475569', 
    marginBottom: 8, 
    lineHeight: 16 
  },
  defectMeta: { 
    flexDirection: 'row', 
    gap: 12, 
    marginBottom: 8,
    flexWrap: 'wrap',
  },
  metaItem: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 4 
  },
  metaText: { 
    fontSize: 11, 
    color: '#64748b', 
    flexShrink: 1 
  },
  thumbnailContainer: {
    position: 'relative',
    width: 60,
    height: 60,
    borderRadius: 8,
    overflow: 'hidden',
    marginTop: 4,
  },
  thumbnail: {
    width: '100%',
    height: '100%',
    backgroundColor: '#f1f5f9',
  },
  thumbnailBadge: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    backgroundColor: 'rgba(0,0,0,0.6)',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
    gap: 2,
  },
  thumbnailBadgeText: {
    fontSize: 8,
    color: '#fff',
    fontWeight: '500',
  },
  cardActions: {
    flexDirection: 'row',
    gap: 8,
    alignItems: 'center',
  },
  mapButton: { 
    width: 32, 
    height: 32, 
    borderRadius: 16, 
    backgroundColor: '#eff6ff', 
    justifyContent: 'center', 
    alignItems: 'center',
  },
  editButton: { 
    width: 32, 
    height: 32, 
    borderRadius: 16, 
    backgroundColor: '#eff6ff', 
    justifyContent: 'center', 
    alignItems: 'center',
  },
  deleteButton: { 
    width: 32, 
    height: 32, 
    borderRadius: 16, 
    backgroundColor: '#fef2f2', 
    justifyContent: 'center', 
    alignItems: 'center',
  },
  
  emptyState: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center', 
    padding: 40, 
    minHeight: 400 
  },
  emptyIconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#f0fdf4',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  emptyTitle: { 
    marginTop: 16, 
    fontSize: 18, 
    fontWeight: '600', 
    color: '#0f172a' 
  },
  emptyText: { 
    marginTop: 8, 
    fontSize: 14, 
    color: '#64748b', 
    textAlign: 'center' 
  },
  createBtn: { 
    marginTop: 24, 
    backgroundColor: '#2563eb', 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 8, 
    paddingHorizontal: 24, 
    paddingVertical: 12, 
    borderRadius: 10 
  },
  createBtnText: { 
    color: '#fff', 
    fontWeight: '600', 
    fontSize: 15 
  },
  
  notAuthContainer: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center', 
    padding: 40 
  },
  notAuthTitle: { 
    marginTop: 16, 
    fontSize: 18, 
    fontWeight: '600', 
    color: '#0f172a' 
  },
  notAuthText: { 
    marginTop: 8, 
    fontSize: 14, 
    color: '#64748b', 
    textAlign: 'center' 
  },
  loginBtn: { 
    marginTop: 24, 
    backgroundColor: '#2563eb', 
    paddingHorizontal: 32, 
    paddingVertical: 12, 
    borderRadius: 10 
  },
  loginBtnText: { 
    color: '#fff', 
    fontWeight: '600', 
    fontSize: 15 
  },
  
  loadingContainer: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  loadingText: { 
    marginTop: 12, 
    fontSize: 14, 
    color: '#64748b' 
  },
});