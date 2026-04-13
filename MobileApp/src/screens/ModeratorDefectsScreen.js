import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, ActivityIndicator, TextInput, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { getPendingDefects, moderateDefect, DEFECT_TYPE_LABELS, SEVERITY_LABELS } from '../services/defectsService';
import { useAuth } from '../context/AuthContext';

export default function ModeratorDefectsScreen({ navigation, route }) {
  const { isModerator } = useAuth();
  const [pendingDefects, setPendingDefects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDefect, setSelectedDefect] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [moderating, setModerating] = useState(false);

  const fetchPending = async () => {
    if (!isModerator) return;
    setLoading(true);
    try {
      const data = await getPendingDefects({ limit: 50 });
      setPendingDefects(data);
    } catch (e) { Alert.alert('Ошибка', 'Не удалось загрузить дефекты'); }
    finally { setLoading(false); }
  };

  useEffect(() => { if (isModerator) fetchPending(); }, [isModerator]);

  const handleModerate = async (defectId, status) => {
    if (status === 'rejected' && !rejectionReason.trim()) return Alert.alert('Требуется причина', 'Укажите причину отклонения');
    setModerating(true);
    try {
      await moderateDefect(defectId, { status, rejection_reason: status === 'rejected' ? rejectionReason.trim() : undefined });
      Alert.alert('Готово', `Дефект ${status === 'approved' ? 'подтверждён' : 'отклонён'}`, [{ text: 'OK', onPress: () => { setSelectedDefect(null); setRejectionReason(''); fetchPending(); }}]);
    } catch (e) { Alert.alert('Ошибка', e.response?.data?.detail || 'Не удалось модерировать'); }
    finally { setModerating(false); }
  };

  if (!isModerator) return <View style={styles.center}><Text style={styles.error}>🚫 Только для модераторов</Text><TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}><Text style={styles.buttonText}>Назад</Text></TouchableOpacity></View>;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => { setSelectedDefect(null); navigation.goBack(); }} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color="#0f172a" /></TouchableOpacity>
        <Text style={styles.title}>{selectedDefect ? 'Модерация' : 'Дефекты на проверке'}</Text>
      </View>

      {selectedDefect ? (
        <ScrollView style={styles.detailScroll}>
          <View style={styles.detailCard}>
            <Text style={styles.detailType}>{DEFECT_TYPE_LABELS[selectedDefect.defect_type] || selectedDefect.defect_type}</Text>
            <Text style={styles.detailDesc}>{selectedDefect.description || 'Нет описания'}</Text>
            <View style={styles.metaRow}><Text style={styles.metaLabel}>Серьёзность:</Text><Text style={[styles.metaValue, { color: selectedDefect.severity === 'critical' ? '#dc2626' : '#475569' }]}>{SEVERITY_LABELS[selectedDefect.severity]}</Text></View>
            <View style={styles.metaRow}><Text style={styles.metaLabel}>Дорога:</Text><Text style={styles.metaValue}>{selectedDefect.road_info?.road_name || 'Не определена'}</Text></View>
            {selectedDefect.photos?.length > 0 && <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.photosRow}>{selectedDefect.photos.map((uri, i) => (<View key={i} style={styles.photoItem}><Image source={{ uri }} style={styles.photoImage} /></View>))}</ScrollView>}
          </View>
          <View style={styles.moderateForm}>
            <Text style={styles.label}>Причина отклонения (если нужно)</Text>
            <TextInput style={styles.input} placeholder="Например: недостаточно информации..." value={rejectionReason} onChangeText={setRejectionReason} multiline numberOfLines={3} />
            <View style={styles.actionsRow}>
              <TouchableOpacity style={[styles.actionBtn, styles.rejectBtn]} onPress={() => handleModerate(selectedDefect.id, 'rejected')} disabled={moderating}><Ionicons name="close-circle" size={20} color="#fff" /><Text style={styles.actionText}>Отклонить</Text></TouchableOpacity>
              <TouchableOpacity style={[styles.actionBtn, styles.approveBtn]} onPress={() => handleModerate(selectedDefect.id, 'approved')} disabled={moderating}>{moderating ? <ActivityIndicator color="#fff" /> : <><Ionicons name="checkmark-circle" size={20} color="#fff" /><Text style={styles.actionText}>Подтвердить</Text></>}</TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      ) : (
        loading ? <ActivityIndicator size="large" color="#2563eb" style={{ marginTop: 40 }} /> :
        pendingDefects.length === 0 ? <View style={styles.emptyState}><Ionicons name="checkmark-done-circle-outline" size={48} color="#22c55e" /><Text style={styles.emptyText}>Нет дефектов на модерацию 🎉</Text></View> :
        <ScrollView>{pendingDefects.map(defect => (
          <TouchableOpacity key={defect.id} style={styles.defectCard} onPress={() => setSelectedDefect(defect)}>
            <View style={styles.defectHeader}><Text style={styles.defectType}>{DEFECT_TYPE_LABELS[defect.defect_type] || defect.defect_type}</Text><Text style={[styles.severityBadge, { backgroundColor: defect.severity === 'critical' ? '#fef2f2' : defect.severity === 'high' ? '#fff7ed' : defect.severity === 'medium' ? '#fffbeb' : '#f0fdf4' }]}>{SEVERITY_LABELS[defect.severity]}</Text></View>
            <Text style={styles.defectDesc} numberOfLines={2}>{defect.description || 'Нет описания'}</Text>
            <View style={styles.defectMeta}><Text style={styles.metaText}>📍 {defect.road_info?.road_name || 'Неизвестно'}</Text><Text style={styles.metaText}>🕐 {new Date(defect.created_at).toLocaleDateString('ru-RU')}</Text></View>
            {defect.photos?.length > 0 && <View style={styles.photosPreview}>{defect.photos.slice(0, 3).map((uri, i) => (<Image key={i} source={{ uri }} style={styles.previewPhoto} />))}{defect.photos.length > 3 && <View style={styles.morePhotos}><Text style={styles.moreText}>+{defect.photos.length - 3}</Text></View>}</View>}
          </TouchableOpacity>
        ))}</ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' }, center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' },
  header: { flexDirection: 'row', alignItems: 'center', padding: 20, paddingBottom: 10, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e2e8f0' },
  backBtn: { padding: 8, marginRight: 12 }, title: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  error: { fontSize: 16, color: '#dc2626', marginBottom: 20 }, button: { backgroundColor: '#2563eb', padding: 12, borderRadius: 10 }, buttonText: { color: '#fff', fontWeight: '600' },
  detailScroll: { flex: 1 }, detailCard: { backgroundColor: '#fff', padding: 16, margin: 16, borderRadius: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  detailType: { fontSize: 18, fontWeight: '700', color: '#0f172a', marginBottom: 8 }, detailDesc: { fontSize: 14, color: '#475569', marginBottom: 16, lineHeight: 20 },
  metaRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 }, metaLabel: { fontSize: 13, color: '#64748b' }, metaValue: { fontSize: 13, fontWeight: '500', color: '#0f172a' },
  photosRow: { flexDirection: 'row', gap: 8, marginTop: 12 }, photoItem: { width: 100, height: 100, borderRadius: 8, overflow: 'hidden' }, photoImage: { width: '100%', height: '100%' },
  moderateForm: { backgroundColor: '#fff', padding: 16, margin: 16, borderRadius: 12, borderWidth: 1, borderColor: '#e2e8f0', marginTop: 8 },
  label: { fontSize: 13, fontWeight: '600', color: '#475569', marginBottom: 8 }, input: { backgroundColor: '#f8fafc', padding: 12, borderRadius: 10, borderWidth: 1, borderColor: '#e2e8f0', minHeight: 80, textAlignVertical: 'top', marginBottom: 16 },
  actionsRow: { flexDirection: 'row', gap: 12 }, actionBtn: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', padding: 14, borderRadius: 10, gap: 6 },
  rejectBtn: { backgroundColor: '#ef4444' }, approveBtn: { backgroundColor: '#22c55e' }, actionText: { color: '#fff', fontWeight: '600' },
  defectCard: { backgroundColor: '#fff', padding: 16, marginHorizontal: 16, marginBottom: 12, borderRadius: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  defectHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }, defectType: { fontSize: 15, fontWeight: '600', color: '#0f172a' },
  severityBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12, fontSize: 11, fontWeight: '600' }, defectDesc: { fontSize: 13, color: '#475569', marginBottom: 12 },
  defectMeta: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 }, metaText: { fontSize: 12, color: '#64748b' },
  photosPreview: { flexDirection: 'row', gap: 4 }, previewPhoto: { width: 50, height: 50, borderRadius: 6 }, morePhotos: { width: 50, height: 50, borderRadius: 6, backgroundColor: '#f1f5f9', justifyContent: 'center', alignItems: 'center' }, moreText: { fontSize: 12, fontWeight: '600', color: '#64748b' },
  emptyState: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40 }, emptyText: { marginTop: 16, fontSize: 15, color: '#64748b', textAlign: 'center' }
});