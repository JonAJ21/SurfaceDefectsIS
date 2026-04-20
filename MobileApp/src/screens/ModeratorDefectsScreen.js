// MobileApp/src/screens/ModeratorDefectsScreen.js
import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView,
  Alert, ActivityIndicator, TextInput, Image, FlatList,
  RefreshControl, Modal
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { defectsApi } from '../config/api';
import { 
  DEFECT_TYPE_LABELS, 
  SEVERITY_LABELS, 
  DEFECT_STATUSES,
  moderateDefect,
  getPendingDefects
} from '../services/defectsService';
import { useAuth } from '../context/AuthContext';
import { formatDate } from '../utils/date';
import { getPhotoUrl } from '../utils/urlHelper';
import PhotoViewerModal from './PhotoViewerModal';

// Компонент модала результата
const ResultModal = ({ visible, title, message, type, onClose }) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <Ionicons name="checkmark-circle" size={48} color="#22c55e" />;
      case 'error':
        return <Ionicons name="close-circle" size={48} color="#dc2626" />;
      default:
        return <Ionicons name="information-circle" size={48} color="#3b82f6" />;
    }
  };

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="fade"
      onRequestClose={onClose}
    >
      <View style={styles.resultOverlay}>
        <View style={styles.resultContainer}>
          {getIcon()}
          <Text style={styles.resultTitle}>{title}</Text>
          <Text style={styles.resultMessage}>{message}</Text>
          <TouchableOpacity style={styles.resultButton} onPress={onClose}>
            <Text style={styles.resultButtonText}>OK</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

// Компонент для отображения дефекта в списке
const DefectListItem = ({ defect, onPress }) => {
  const severityColor = {
    critical: '#dc2626',
    high: '#f97316',
    medium: '#f59e0b',
    low: '#22c55e'
  }[defect.severity] || '#64748b';

  const statusColors = {
    pending: { bg: '#fffbeb', text: '#f59e0b', icon: 'time-outline' },
    approved: { bg: '#f0fdf4', text: '#16a34a', icon: 'checkmark-circle-outline' },
    rejected: { bg: '#fef2f2', text: '#dc2626', icon: 'close-circle-outline' },
    fixed: { bg: '#eff6ff', text: '#3b82f6', icon: 'checkmark-done-circle-outline' }
  };

  const statusStyle = statusColors[defect.status] || statusColors.pending;

  return (
    <TouchableOpacity style={styles.defectCard} onPress={() => onPress(defect)}>
      <View style={styles.defectHeader}>
        <View style={styles.defectTypeContainer}>
          <Text style={styles.defectType} numberOfLines={1}>
            {DEFECT_TYPE_LABELS[defect.defect_type] || defect.defect_type}
          </Text>
          <View style={[styles.severityBadge, { backgroundColor: severityColor + '20' }]}>
            <View style={[styles.severityDot, { backgroundColor: severityColor }]} />
            <Text style={[styles.severityText, { color: severityColor }]}>
              {SEVERITY_LABELS[defect.severity]}
            </Text>
          </View>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: statusStyle.bg }]}>
          <Ionicons name={statusStyle.icon} size={12} color={statusStyle.text} />
          <Text style={[styles.statusText, { color: statusStyle.text }]}>
            {statusStyle.text === 'fixed' ? 'Исправлен' : 
             statusStyle.text === 'approved' ? 'Подтверждён' :
             statusStyle.text === 'rejected' ? 'Отклонён' : 'На модерации'}
          </Text>
        </View>
      </View>

      {defect.description && (
        <Text style={styles.defectDesc} numberOfLines={2}>{defect.description}</Text>
      )}

      <View style={styles.defectMeta}>
        <View style={styles.metaItem}>
          <Ionicons name="location-outline" size={12} color="#94a3b8" />
          <Text style={styles.metaText} numberOfLines={1}>
            {defect.road_info?.road_name || defect.road_name || 'Неизвестно'}
          </Text>
        </View>
        <View style={styles.metaItem}>
          <Ionicons name="person-outline" size={12} color="#94a3b8" />
          <Text style={styles.metaText} numberOfLines={1}>
            {defect.created_by || 'Неизвестно'}
          </Text>
        </View>
        <View style={styles.metaItem}>
          <Ionicons name="time-outline" size={12} color="#94a3b8" />
          <Text style={styles.metaText}>{formatDate(defect.created_at)}</Text>
        </View>
      </View>

      {defect.photos?.length > 0 && (
        <View style={styles.photosPreview}>
          {defect.photos.slice(0, 3).map((uri, i) => (
            <Image key={i} source={{ uri: getPhotoUrl(uri) }} style={styles.previewPhoto} />
          ))}
          {defect.photos.length > 3 && (
            <View style={styles.morePhotos}>
              <Text style={styles.moreText}>+{defect.photos.length - 3}</Text>
            </View>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
};

// Компонент модала модерации
const ModerateModal = ({ visible, defect, onClose, onModerate, loading }) => {
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    if (!visible) {
      setRejectionReason('');
    }
  }, [visible]);

  if (!defect) return null;

  const severityColor = {
    critical: '#dc2626',
    high: '#f97316',
    medium: '#f59e0b',
    low: '#22c55e'
  }[defect.severity] || '#64748b';

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Модерация дефекта</Text>
            <TouchableOpacity onPress={onClose} style={styles.modalCloseBtn}>
              <Ionicons name="close" size={24} color="#64748b" />
            </TouchableOpacity>
          </View>

          <ScrollView showsVerticalScrollIndicator={false}>
            <View style={styles.modalDefectInfo}>
              <Text style={styles.modalDefectType}>
                {DEFECT_TYPE_LABELS[defect.defect_type] || defect.defect_type}
              </Text>
              <View style={[styles.modalSeverityBadge, { backgroundColor: severityColor + '20' }]}>
                <View style={[styles.severityDot, { backgroundColor: severityColor }]} />
                <Text style={[styles.modalSeverityText, { color: severityColor }]}>
                  {SEVERITY_LABELS[defect.severity]}
                </Text>
              </View>
            </View>

            {defect.description && (
              <Text style={styles.modalDescription}>{defect.description}</Text>
            )}

            <View style={styles.modalInfoRow}>
              <Ionicons name="location-outline" size={16} color="#64748b" />
              <Text style={styles.modalInfoText}>
                {defect.road_info?.road_name || defect.road_name || 'Дорога не определена'}
              </Text>
            </View>

            <View style={styles.modalInfoRow}>
              <Ionicons name="person-outline" size={16} color="#64748b" />
              <Text style={styles.modalInfoText}>
                Создатель: {defect.created_by || 'Неизвестно'}
              </Text>
            </View>

            <View style={styles.modalInfoRow}>
              <Ionicons name="time-outline" size={16} color="#64748b" />
              <Text style={styles.modalInfoText}>{formatDate(defect.created_at)}</Text>
            </View>

            {defect.photos?.length > 0 && (
              <View style={styles.modalPhotos}>
                <Text style={styles.modalPhotosTitle}>Фотографии ({defect.photos.length})</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {defect.photos.map((uri, i) => (
                    <Image key={i} source={{ uri: getPhotoUrl(uri) }} style={styles.modalPhoto} />
                  ))}
                </ScrollView>
              </View>
            )}

            <View style={styles.modalRejectSection}>
              <Text style={styles.modalRejectLabel}>Причина отклонения (если нужно)</Text>
              <TextInput
                style={styles.modalRejectInput}
                placeholder="Например: недостаточно информации, неверные координаты..."
                value={rejectionReason}
                onChangeText={setRejectionReason}
                multiline
                numberOfLines={3}
                textAlignVertical="top"
              />
            </View>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={[styles.modalActionBtn, styles.modalRejectBtn]}
                onPress={() => onModerate(defect.id, 'rejected', rejectionReason)}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator size="small" color="#fff" />
                ) : (
                  <>
                    <Ionicons name="close-circle" size={20} color="#fff" />
                    <Text style={styles.modalActionText}>Отклонить</Text>
                  </>
                )}
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalActionBtn, styles.modalApproveBtn]}
                onPress={() => onModerate(defect.id, 'approved')}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator size="small" color="#fff" />
                ) : (
                  <>
                    <Ionicons name="checkmark-circle" size={20} color="#fff" />
                    <Text style={styles.modalActionText}>Подтвердить</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
};

export default function ModeratorDefectsScreen({ navigation, route }) {
  const { isModerator } = useAuth();
  const { status: initialStatus = 'pending' } = route.params || {};
  
  const [defects, setDefects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedDefect, setSelectedDefect] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [moderating, setModerating] = useState(false);
  const [filter, setFilter] = useState(initialStatus);
  const [searchQuery, setSearchQuery] = useState('');
  const [photoViewerVisible, setPhotoViewerVisible] = useState(false);
  const [photoViewerPhotos, setPhotoViewerPhotos] = useState([]);
  const [photoViewerIndex, setPhotoViewerIndex] = useState(0);
  const [resultModalVisible, setResultModalVisible] = useState(false);
  const [resultData, setResultData] = useState({ title: '', message: '', type: 'success' });
  
  // Пагинация
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const PAGE_SIZE = 20;

  const fetchDefects = useCallback(async (refresh = false) => {
    if (!isModerator) return;
    
    const currentOffset = refresh ? 0 : offset;
    
    if (refresh) {
      setLoading(true);
      setOffset(0);
    } else if (currentOffset > 0) {
      setLoadingMore(true);
    }
    
    try {
      let data = [];
      
      if (filter === 'pending') {
        data = await getPendingDefects({ limit: PAGE_SIZE, offset: currentOffset });
      } else {
        const params = new URLSearchParams();
        params.append('limit', PAGE_SIZE);
        params.append('offset', currentOffset);
        
        if (filter !== 'all') {
          // Правильный формат: defect_statuses=approved (как строка, не массив)
          params.append('defect_statuses', filter);
        }
        
        const response = await defectsApi.get(`/v1/defects?${params.toString()}`);
        data = response.data || [];
      }
      
      if (refresh) {
        setDefects(data);
        setOffset(PAGE_SIZE);
        setHasMore(data.length === PAGE_SIZE);
      } else {
        setDefects(prev => [...prev, ...data]);
        setOffset(currentOffset + PAGE_SIZE);
        setHasMore(data.length === PAGE_SIZE);
      }
    } catch (error) {
      console.error('Fetch defects error:', error);
      Alert.alert('Ошибка', 'Не удалось загрузить дефекты');
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  }, [isModerator, filter, offset]);

  useEffect(() => {
    if (isModerator) {
      fetchDefects(true);
    }
  }, [isModerator, filter]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchDefects(true);
  };

  const loadMore = () => {
    if (!loadingMore && hasMore && !loading) {
      fetchDefects(false);
    }
  };

  const handleDefectPress = (defect) => {
    setSelectedDefect(defect);
    setModalVisible(true);
  };

  const handleModerate = async (defectId, status, rejectionReason = '') => {
    if (status === 'rejected' && !rejectionReason.trim()) {
      Alert.alert('Требуется причина', 'Укажите причину отклонения дефекта');
      return;
    }
    
    setModerating(true);
    try {
      await moderateDefect(defectId, { 
        status, 
        rejection_reason: status === 'rejected' ? rejectionReason.trim() : undefined 
      });
      
      setModalVisible(false);
      setSelectedDefect(null);
      
      setResultData({
        title: 'Успешно',
        message: `Дефект ${status === 'approved' ? 'подтверждён' : 'отклонён'}`,
        type: 'success'
      });
      setResultModalVisible(true);
    } catch (error) {
      console.error('Moderate error:', error);
      
      let errorMessage = 'Не удалось модерировать дефект';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map(d => d.msg).join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        }
      }
      
      setResultData({
        title: 'Ошибка',
        message: errorMessage,
        type: 'error'
      });
      setResultModalVisible(true);
    } finally {
      setModerating(false);
    }
  };

  const handleResultClose = () => {
    setResultModalVisible(false);
    fetchDefects(true);
  };

  const handlePhotoPress = (photos, index) => {
    setPhotoViewerPhotos(photos);
    setPhotoViewerIndex(index);
    setPhotoViewerVisible(true);
  };

  const filteredDefects = defects.filter(defect => {
    if (searchQuery) {
      const typeMatch = DEFECT_TYPE_LABELS[defect.defect_type]?.toLowerCase().includes(searchQuery.toLowerCase());
      const descMatch = defect.description?.toLowerCase().includes(searchQuery.toLowerCase());
      const roadMatch = defect.road_info?.road_name?.toLowerCase().includes(searchQuery.toLowerCase());
      return typeMatch || descMatch || roadMatch;
    }
    return true;
  });

  const getStatusTitle = () => {
    switch (filter) {
      case 'pending': return 'На модерации';
      case 'approved': return 'Подтверждённые';
      case 'rejected': return 'Отклонённые';
      case 'fixed': return 'Исправленные';
      default: return 'Все дефекты';
    }
  };

  const filterOptions = [
    { value: 'pending', label: 'На модерации', icon: 'time-outline', color: '#f59e0b' },
    { value: 'approved', label: 'Подтверждённые', icon: 'checkmark-circle-outline', color: '#16a34a' },
    { value: 'rejected', label: 'Отклонённые', icon: 'close-circle-outline', color: '#dc2626' },
    { value: 'fixed', label: 'Исправленные', icon: 'checkmark-done-circle-outline', color: '#3b82f6' },
    { value: 'all', label: 'Все', icon: 'list-outline', color: '#64748b' },
  ];

  if (!isModerator) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>🚫 Только для модераторов</Text>
        <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
          <Text style={styles.buttonText}>Назад</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#0f172a" />
        </TouchableOpacity>
        <Text style={styles.title}>{getStatusTitle()}</Text>
        <TouchableOpacity onPress={onRefresh} style={styles.refreshBtn}>
          <Ionicons name="refresh-outline" size={22} color="#2563eb" />
        </TouchableOpacity>
      </View>

      {/* Поиск */}
      <View style={styles.searchContainer}>
        <Ionicons name="search-outline" size={20} color="#94a3b8" />
        <TextInput
          style={styles.searchInput}
          placeholder="Поиск по типу, описанию или дороге..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor="#94a3b8"
        />
        {searchQuery !== '' && (
          <TouchableOpacity onPress={() => setSearchQuery('')}>
            <Ionicons name="close-circle" size={18} color="#94a3b8" />
          </TouchableOpacity>
        )}
      </View>

      {/* Фильтры */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        style={styles.filtersContainer}
        contentContainerStyle={styles.filtersContent}
      >
        {filterOptions.map(option => (
          <TouchableOpacity
            key={option.value}
            style={[
              styles.filterChip,
              filter === option.value && { backgroundColor: option.color + '15', borderColor: option.color }
            ]}
            onPress={() => {
              setFilter(option.value);
              setOffset(0);
              setHasMore(true);
            }}
          >
            <Ionicons name={option.icon} size={14} color={filter === option.value ? option.color : '#64748b'} />
            <Text style={[styles.filterText, filter === option.value && { color: option.color }]}>
              {option.label}
            </Text>
            {filter === option.value && (
              <View style={[styles.filterActiveDot, { backgroundColor: option.color }]} />
            )}
          </TouchableOpacity>
        ))}
      </ScrollView>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563eb" />
          <Text style={styles.loadingText}>Загрузка дефектов...</Text>
        </View>
      ) : filteredDefects.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="checkmark-done-circle-outline" size={64} color="#22c55e" />
          <Text style={styles.emptyTitle}>Нет дефектов</Text>
          <Text style={styles.emptyText}>
            {filter === 'pending' ? 'Нет дефектов, ожидающих модерации' :
             filter === 'approved' ? 'Нет подтверждённых дефектов' :
             filter === 'rejected' ? 'Нет отклонённых дефектов' :
             filter === 'fixed' ? 'Нет исправленных дефектов' :
             'Дефекты не найдены'}
          </Text>
        </View>
      ) : (
        <FlatList
          data={filteredDefects}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <DefectListItem defect={item} onPress={handleDefectPress} />
          )}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          onEndReached={loadMore}
          onEndReachedThreshold={0.3}
          ListFooterComponent={
            loadingMore ? (
              <View style={styles.footerLoader}>
                <ActivityIndicator size="small" color="#2563eb" />
                <Text style={styles.footerText}>Загрузка ещё...</Text>
              </View>
            ) : hasMore && defects.length > 0 ? (
              <View style={styles.footerLoader}>
                <Text style={styles.footerText}>Потяните вверх для загрузки ещё</Text>
              </View>
            ) : defects.length > 0 ? (
              <View style={styles.footerLoader}>
                <Text style={styles.footerEndText}>Все дефекты загружены</Text>
              </View>
            ) : null
          }
          showsVerticalScrollIndicator={false}
        />
      )}

      <ModerateModal
        visible={modalVisible}
        defect={selectedDefect}
        onClose={() => {
          setModalVisible(false);
          setSelectedDefect(null);
        }}
        onModerate={handleModerate}
        loading={moderating}
      />

      <ResultModal
        visible={resultModalVisible}
        title={resultData.title}
        message={resultData.message}
        type={resultData.type}
        onClose={handleResultClose}
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
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' },
  
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  backBtn: { padding: 8, borderRadius: 8, backgroundColor: '#f8fafc', borderWidth: 1, borderColor: '#e2e8f0' },
  title: { fontSize: 18, fontWeight: '700', color: '#0f172a', flex: 1, marginLeft: 12 },
  refreshBtn: { padding: 8, borderRadius: 8, backgroundColor: '#f8fafc', borderWidth: 1, borderColor: '#e2e8f0' },
  
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    margin: 16,
    marginBottom: 8,
    paddingHorizontal: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    gap: 8,
  },
  searchInput: { flex: 1, paddingVertical: 10, fontSize: 14, color: '#0f172a' },
  
  filtersContainer: { 
    marginBottom: 12,
    maxHeight: 44,
  },
  filtersContent: { 
    paddingHorizontal: 16, 
    gap: 8,
    alignItems: 'center',
  },
  filterChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#fff',
    gap: 6,
  },
  filterText: { 
    fontSize: 13, 
    fontWeight: '500', 
    color: '#64748b',
  },
  filterActiveDot: { 
    width: 6, 
    height: 6, 
    borderRadius: 3,
  },
  
  listContent: { padding: 16, paddingTop: 8, paddingBottom: 40 },
  
  defectCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    padding: 14,
    marginBottom: 12,
  },
  defectHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 },
  defectTypeContainer: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
  defectType: { fontSize: 15, fontWeight: '600', color: '#0f172a' },
  severityBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 8 },
  severityDot: { width: 6, height: 6, borderRadius: 3 },
  severityText: { fontSize: 10, fontWeight: '600' },
  statusBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 12 },
  statusText: { fontSize: 10, fontWeight: '600' },
  defectDesc: { fontSize: 13, color: '#475569', marginBottom: 10, lineHeight: 18 },
  defectMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 10 },
  metaItem: { flexDirection: 'row', alignItems: 'center', gap: 4, flexShrink: 1 },
  metaText: { fontSize: 11, color: '#64748b', flexShrink: 1 },
  photosPreview: { flexDirection: 'row', gap: 6, marginTop: 4 },
  previewPhoto: { width: 50, height: 50, borderRadius: 8, backgroundColor: '#f1f5f9' },
  morePhotos: { width: 50, height: 50, borderRadius: 8, backgroundColor: '#f1f5f9', justifyContent: 'center', alignItems: 'center' },
  moreText: { fontSize: 12, fontWeight: '600', color: '#64748b' },
  
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContainer: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '90%',
    padding: 20,
  },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modalTitle: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  modalCloseBtn: { padding: 4 },
  modalDefectInfo: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 12, flexWrap: 'wrap' },
  modalDefectType: { fontSize: 18, fontWeight: '700', color: '#0f172a', flex: 1 },
  modalSeverityBadge: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  modalSeverityText: { fontSize: 12, fontWeight: '600' },
  modalDescription: { fontSize: 14, color: '#475569', marginBottom: 16, lineHeight: 20 },
  modalInfoRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 12 },
  modalInfoText: { flex: 1, fontSize: 13, color: '#64748b' },
  modalPhotos: { marginTop: 8, marginBottom: 16 },
  modalPhotosTitle: { fontSize: 14, fontWeight: '600', color: '#334155', marginBottom: 8 },
  modalPhoto: { width: 100, height: 100, borderRadius: 8, marginRight: 8, backgroundColor: '#f1f5f9' },
  modalRejectSection: { marginBottom: 20 },
  modalRejectLabel: { fontSize: 13, fontWeight: '600', color: '#475569', marginBottom: 8 },
  modalRejectInput: {
    backgroundColor: '#f8fafc',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    minHeight: 80,
    textAlignVertical: 'top',
    fontSize: 13,
    color: '#0f172a',
  },
  modalActions: { flexDirection: 'row', gap: 12, marginBottom: 10 },
  modalActionBtn: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', padding: 14, borderRadius: 12, gap: 8 },
  modalRejectBtn: { backgroundColor: '#ef4444' },
  modalApproveBtn: { backgroundColor: '#22c55e' },
  modalActionText: { color: '#fff', fontWeight: '600', fontSize: 14 },
  
  resultOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  resultContainer: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    width: '80%',
    maxWidth: 280,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0f172a',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  resultMessage: {
    fontSize: 14,
    color: '#475569',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  resultButton: {
    backgroundColor: '#2563eb',
    paddingHorizontal: 32,
    paddingVertical: 10,
    borderRadius: 10,
  },
  resultButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 12, fontSize: 14, color: '#64748b' },
  
  emptyState: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40 },
  emptyTitle: { fontSize: 18, fontWeight: '600', color: '#0f172a', marginTop: 16, marginBottom: 8 },
  emptyText: { fontSize: 14, color: '#64748b', textAlign: 'center' },
  
  footerLoader: { paddingVertical: 20, alignItems: 'center' },
  footerText: { fontSize: 12, color: '#94a3b8' },
  footerEndText: { fontSize: 12, color: '#22c55e' },
  
  error: { fontSize: 16, color: '#dc2626', textAlign: 'center', marginTop: 100, marginBottom: 20 },
  button: { backgroundColor: '#2563eb', padding: 14, borderRadius: 10, alignItems: 'center', marginHorizontal: 20 },
  buttonText: { color: '#fff', fontWeight: '600' },
});