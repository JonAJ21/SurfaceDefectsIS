// MobileApp/src/components/DefectPopup.js
import React from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, Image,
  Modal, ScrollView, Dimensions, Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { getPhotoUrl } from '../utils/urlHelper';
import { DEFECT_TYPE_LABELS, SEVERITY_LABELS } from '../services/defectsService';
import { formatDate } from '../utils/date';

const { width, height } = Dimensions.get('window');

export default function DefectPopup({ visible, defect, onClose, onNavigate }) {
  if (!defect) return null;

  const severityColor = {
    low: '#22c55e',
    medium: '#f59e0b',
    high: '#f97316',
    critical: '#dc2626'
  }[defect.severity] || '#64748b';

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <TouchableOpacity style={styles.backdrop} activeOpacity={1} onPress={onClose} />
        
        <View style={styles.container}>
          {/* Заголовок */}
          <View style={styles.header}>
            <View style={[styles.severityBadge, { backgroundColor: severityColor + '20' }]}>
              <View style={[styles.severityDot, { backgroundColor: severityColor }]} />
              <Text style={[styles.severityText, { color: severityColor }]}>
                {SEVERITY_LABELS[defect.severity] || defect.severity}
              </Text>
            </View>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Ionicons name="close" size={24} color="#64748b" />
            </TouchableOpacity>
          </View>

          <ScrollView showsVerticalScrollIndicator={false}>
            {/* Тип дефекта */}
            <Text style={styles.defectType}>
              {DEFECT_TYPE_LABELS[defect.defect_type] || defect.defect_type}
            </Text>

            {/* Описание */}
            {defect.description ? (
              <Text style={styles.description}>{defect.description}</Text>
            ) : (
              <Text style={styles.noDescription}>Нет описания</Text>
            )}

            {/* Информация о дороге */}
            {defect.road_name && (
              <View style={styles.infoRow}>
                <Ionicons name="location-outline" size={18} color="#64748b" />
                <Text style={styles.infoText}>{defect.road_name}</Text>
              </View>
            )}

            {/* Статус */}
            <View style={styles.infoRow}>
              <Ionicons name="time-outline" size={18} color="#64748b" />
              <Text style={styles.infoText}>
                {formatDate(defect.created_at)}
              </Text>
            </View>

            <View style={styles.infoRow}>
              <Ionicons name="flag-outline" size={18} color="#64748b" />
              <Text style={styles.infoText}>
                Статус: {defect.status === 'pending' ? 'На модерации' : 
                         defect.status === 'approved' ? 'Подтверждён' :
                         defect.status === 'rejected' ? 'Отклонён' : 'Исправлен'}
              </Text>
            </View>

            {/* Фотографии */}
            {defect.photos && defect.photos.length > 0 && (
              <View style={styles.photosSection}>
                <Text style={styles.sectionTitle}>Фотографии ({defect.photos.length})</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.photosScroll}>
                  {defect.photos.map((photo, index) => (
                    <TouchableOpacity 
                      key={index} 
                      style={styles.photoItem}
                      onPress={() => {
                        // Открыть просмотр фото
                      }}
                    >
                      <Image 
                        source={{ uri: getPhotoUrl(photo) }} 
                        style={styles.photo}
                        resizeMode="cover"
                      />
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>
            )}

            {/* Кнопка навигации */}
            <TouchableOpacity 
              style={styles.navigateBtn}
              onPress={() => {
                onClose();
                if (defect.lat && defect.lon) {
                  onNavigate(defect.lat, defect.lon);
                }
              }}
            >
              <Ionicons name="navigate" size={20} color="#fff" />
              <Text style={styles.navigateBtnText}>Показать на карте</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  container: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: height * 0.8,
    padding: 20,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -2 },
        shadowOpacity: 0.1,
        shadowRadius: 10,
      },
      android: {
        elevation: 10,
      },
    }),
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  severityBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20,
    gap: 6,
  },
  severityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  severityText: {
    fontSize: 12,
    fontWeight: '600',
  },
  closeBtn: {
    padding: 4,
  },
  defectType: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 12,
  },
  description: {
    fontSize: 15,
    color: '#475569',
    lineHeight: 22,
    marginBottom: 16,
  },
  noDescription: {
    fontSize: 14,
    color: '#94a3b8',
    fontStyle: 'italic',
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 12,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#64748b',
  },
  photosSection: {
    marginTop: 8,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#334155',
    marginBottom: 12,
  },
  photosScroll: {
    flexDirection: 'row',
  },
  photoItem: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginRight: 10,
    overflow: 'hidden',
    backgroundColor: '#f1f5f9',
  },
  photo: {
    width: '100%',
    height: '100%',
  },
  navigateBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2563eb',
    padding: 14,
    borderRadius: 12,
    gap: 8,
    marginTop: 8,
    marginBottom: Platform.OS === 'ios' ? 20 : 10,
  },
  navigateBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});