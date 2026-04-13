import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { formatDate } from '../utils/date'; // 🔹 Импорт утилиты

export default function ProfileScreen({ navigation }) {
  const { user, isAuthenticated, verifyEmail, logout, loading, apiError, successMessage, isAdmin, isModerator } = useAuth();
  const [showAllSessions, setShowAllSessions] = useState(false);

  const handleLogout = async (allSessions = false) => {
    await logout(allSessions);
    navigation.reset({ index: 0, routes: [{ name: 'Map' }] });
  };

  if (!isAuthenticated) {
    return (
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color="#0f172a" /></TouchableOpacity>
          <Text style={styles.title}>Профиль</Text>
        </View>
        <View style={styles.emptyState}>
          <Ionicons name="person-remove-outline" size={48} color="#94a3b8" />
          <Text style={styles.emptyText}>Вы не авторизованы</Text>
          <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Login')}>
            <Text style={styles.buttonText}>Войти в систему</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    );
  }

  const sessions = user?.sessions || [];
  const currentSessionOid = user?.currentSessionOid;
  const currentSession = sessions.find(s => s.oid === currentSessionOid);
  const otherSessions = sessions.filter(s => s.oid !== currentSessionOid);

  return (
    <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color="#0f172a" /></TouchableOpacity>
        <Text style={styles.title}>Мой профиль</Text>
      </View>

      {successMessage && <View style={[styles.messageBox, styles.successBox]}><Text style={styles.successText}>{successMessage}</Text></View>}
      {apiError && <View style={[styles.messageBox, styles.errorBox]}><Text style={styles.errorText}>{apiError}</Text></View>}

      <View style={styles.card}>
        <Text style={styles.label}>Email</Text>
        <View style={styles.row}>
          <Text style={styles.value}>{user?.email}</Text>
          {user?.is_verified ? (
            <View style={styles.verifiedBadge}><Ionicons name="checkmark-circle" size={16} color="#16a34a" /><Text style={styles.verifiedText}>Верифицирован</Text></View>
          ) : (
            <View style={styles.unverifiedBadge}><Ionicons name="alert-circle" size={16} color="#f59e0b" /><Text style={styles.unverifiedText}>Не верифицирован</Text></View>
          )}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Роли</Text>
        <View style={styles.chipContainer}>
          {user?.roles?.length > 0 ? user.roles.map(role => (
            <View key={role.oid} style={styles.chip}><Text style={styles.chipText}>{role.name}</Text></View>
          )) : <Text style={styles.placeholder}>Нет назначенных ролей</Text>}
        </View>
      </View>

      {(isAdmin || isModerator) && (
        <View style={styles.card}>
          <Text style={styles.label}>🛠️ Панели управления</Text>
          <View style={styles.panelGrid}>
            {isAdmin && (
              <TouchableOpacity style={[styles.panelBtn, styles.adminPanelBtn]} onPress={() => navigation.navigate('AdminDashboard')}>
                <Ionicons name="shield-checkmark" size={24} color="#fff" />
                <Text style={styles.panelBtnText}>Админ-панель</Text>
              </TouchableOpacity>
            )}
            {isModerator && (
              <TouchableOpacity style={[styles.panelBtn, styles.modPanelBtn]} onPress={() => navigation.navigate('ModeratorDashboard')}>
                <Ionicons name="checkmark-done" size={24} color="#fff" />
                <Text style={styles.panelBtnText}>Модерация дефектов</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.label}>🖥️ Сессии</Text>
        {currentSession && (
          <>
            <View style={[styles.sessionItem, styles.currentSession]}>
              <View style={styles.sessionHeader}>
                <Text style={styles.sessionDevice}>{currentSession.user_agent || 'Неизвестное устройство'}</Text>
                <View style={styles.currentBadge}><Text style={styles.currentBadgeText}>Текущая</Text></View>
              </View>
              <View style={styles.sessionMeta}>
                {/* 🔹 Теперь используется formatDate из утилиты */}
                <Text style={styles.sessionText}>Создана: {formatDate(currentSession.created_at)}</Text>
                <Text style={styles.sessionText}>Обновлена: {formatDate(currentSession.refreshed_at)}</Text>
              </View>
            </View>
            {otherSessions.length > 0 && (
              <TouchableOpacity style={styles.toggleSessionsBtn} onPress={() => setShowAllSessions(!showAllSessions)}>
                <Ionicons name={showAllSessions ? 'chevron-up' : 'chevron-down'} size={18} color="#2563eb" />
                <Text style={styles.toggleSessionsText}>{showAllSessions ? 'Скрыть остальные' : `Показать остальные (${otherSessions.length})`}</Text>
              </TouchableOpacity>
            )}
            {showAllSessions && otherSessions.map(session => (
              <View key={session.oid} style={styles.sessionItem}>
                <Text style={styles.sessionDevice}>{session.user_agent || 'Неизвестное устройство'}</Text>
                <View style={styles.sessionMeta}>
                  <Text style={styles.sessionText}>Создана: {formatDate(session.created_at)}</Text>
                  <Text style={styles.sessionText}>Обновлена: {formatDate(session.refreshed_at)}</Text>
                </View>
              </View>
            ))}
          </>
        )}
      </View>

      {!user?.is_verified && (
        <TouchableOpacity style={styles.actionButton} onPress={verifyEmail} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : (<><Ionicons name="mail-outline" size={20} color="#fff" /><Text style={styles.actionButtonText}>Отправить письмо подтверждения</Text></>)}
        </TouchableOpacity>
      )}

      <View style={styles.divider} />
      <TouchableOpacity style={[styles.actionButton, styles.logoutBtn]} onPress={() => handleLogout(false)} disabled={loading}>
        <Ionicons name="log-out-outline" size={20} color="#fff" /><Text style={styles.actionButtonText}>Выйти из текущей сессии</Text>
      </TouchableOpacity>
      <TouchableOpacity style={[styles.actionButton, styles.logoutAllBtn]} onPress={() => handleLogout(true)} disabled={loading}>
        <Ionicons name="close-circle-outline" size={20} color="#fff" /><Text style={styles.actionButtonText}>Выйти со всех устройств</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: '#f8fafc', padding: 20, paddingBottom: 40 },
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  backBtn: { padding: 8, marginRight: 12, borderRadius: 8, backgroundColor: '#fff', borderWidth: 1, borderColor: '#e2e8f0' },
  title: { fontSize: 24, fontWeight: '700', color: '#0f172a' },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 16, marginBottom: 16, borderWidth: 1, borderColor: '#e2e8f0' },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  label: { fontSize: 13, fontWeight: '500', color: '#64748b', marginBottom: 6 },
  value: { fontSize: 15, fontWeight: '600', color: '#0f172a' },
  verifiedBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f0fdf4', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12, gap: 4 },
  verifiedText: { fontSize: 12, fontWeight: '500', color: '#166534' },
  unverifiedBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fffbeb', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12, gap: 4 },
  unverifiedText: { fontSize: 12, fontWeight: '500', color: '#b45309' },
  divider: { height: 1, backgroundColor: '#f1f5f9', marginVertical: 12 },
  chipContainer: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: { backgroundColor: '#eff6ff', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 20, borderWidth: 1, borderColor: '#bfdbfe' },
  chipText: { fontSize: 13, fontWeight: '500', color: '#1e40af' },
  placeholder: { fontSize: 13, color: '#94a3b8', fontStyle: 'italic' },
  panelGrid: { flexDirection: 'row', gap: 12, marginTop: 8 },
  panelBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 14, borderRadius: 12, gap: 8 },
  adminPanelBtn: { backgroundColor: '#7c3aed' },
  modPanelBtn: { backgroundColor: '#059669' },
  panelBtnText: { color: '#fff', fontWeight: '600', fontSize: 14 },
  sessionItem: { backgroundColor: '#f8fafc', padding: 12, borderRadius: 10, borderWidth: 1, borderColor: '#e2e8f0', marginBottom: 10 },
  currentSession: { backgroundColor: '#eff6ff', borderColor: '#bfdbfe' },
  sessionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  sessionDevice: { fontSize: 14, fontWeight: '600', color: '#334155' },
  currentBadge: { backgroundColor: '#2563eb', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 8 },
  currentBadgeText: { fontSize: 10, fontWeight: '700', color: '#fff', textTransform: 'uppercase' },
  sessionMeta: { gap: 2 },
  sessionText: { fontSize: 12, color: '#64748b' },
  toggleSessionsBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 10, gap: 6 },
  toggleSessionsText: { fontSize: 13, fontWeight: '600', color: '#2563eb' },
  messageBox: { padding: 10, borderRadius: 10, marginBottom: 12, borderWidth: 1 },
  successBox: { backgroundColor: '#f0fdf4', borderColor: '#bbf7d0' },
  successText: { color: '#166534', textAlign: 'center', fontSize: 13 },
  errorBox: { backgroundColor: '#fef2f2', borderColor: '#fecaca' },
  errorText: { color: '#dc2626', textAlign: 'center', fontSize: 13 },
  actionButton: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', backgroundColor: '#2563eb', padding: 14, borderRadius: 12, marginBottom: 12 },
  logoutBtn: { backgroundColor: '#ef4444' },
  logoutAllBtn: { backgroundColor: '#f97316' },
  actionButtonText: { color: '#fff', fontWeight: '600', marginLeft: 8, fontSize: 15 },
  emptyState: { flex: 1, justifyContent: 'center', alignItems: 'center', marginTop: 40 },
  emptyText: { fontSize: 16, color: '#64748b', marginTop: 12, marginBottom: 20 },
  button: { backgroundColor: '#2563eb', padding: 14, borderRadius: 12, width: '100%', alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '600' }
});