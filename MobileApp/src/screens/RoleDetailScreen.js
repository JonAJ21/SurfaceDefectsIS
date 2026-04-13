import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Switch } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authApi } from '../config/api';

export default function RoleDetailScreen({ route, navigation }) {
  const { roleIdentifier } = route.params;
  const [role, setRole] = useState(null);
  const [allPermissions, setAllPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  // Загрузка всех разрешений и данных роли
  const fetchData = async () => {
    setLoading(true);
    try {
      // Получаем все доступные разрешения
      const permsResponse = await authApi.get('/v1/permissions', { params: { limit: 100 } });
      const perms = Array.isArray(permsResponse.data) 
        ? permsResponse.data 
        : (permsResponse.data.permissions || permsResponse.data.data?.permissions || []);
      
      // Получаем роль с её разрешениями
      const roleResponse = await authApi.get(`/v1/roles/${roleIdentifier}`, { 
        params: { load_permissions: true } 
      });
      
      setAllPermissions(perms);
      setRole(roleResponse.data);
    } catch (e) {
      console.error('❌ Fetch error:', e.response?.data || e.message);
      Alert.alert('Ошибка', 'Не удалось загрузить данные');
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => { fetchData(); }, []);

  // Проверка, есть ли разрешение у роли
  const hasPermission = (perm) => {
    if (!role?.permissions) return false;
    return role.permissions.some(p => p.oid === perm.oid || p.code === perm.code);
  };

  // Переключение разрешения (assign/revoke)
  const togglePermission = async (perm) => {
    if (actionLoading) return;
    
    const isAssigned = hasPermission(perm);
    const permIdentifier = perm.oid ? `oid_${perm.oid}` : `code_${perm.code}`;
    
    console.log(`🔄 Toggle permission ${perm.code}: ${isAssigned ? 'REVOKE' : 'ASSIGN'}`);
    
    setActionLoading(true);
    try {
      if (isAssigned) {
        // Отозвать разрешение
        await authApi.delete(`/v1/roles/${roleIdentifier}/permissions/${permIdentifier}`);
        console.log(`✅ Revoked ${perm.code}`);
      } else {
        // Назначить разрешение
        await authApi.post(`/v1/roles/${roleIdentifier}/permissions/${permIdentifier}`);
        console.log(`✅ Assigned ${perm.code}`);
      }
      
      // Обновляем данные роли
      await fetchData();
    } catch (e) {
      console.error('❌ Toggle failed:', e.response?.data || e.message);
      Alert.alert(
        'Ошибка', 
        isAssigned 
          ? `Не удалось отозвать разрешение ${perm.code}`
          : `Не удалось назначить разрешение ${perm.code}`
      );
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#2563eb" />
        <Text style={styles.loadingText}>Загрузка...</Text>
      </View>
    );
  }

  if (!role) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Не удалось загрузить роль</Text>
        <TouchableOpacity style={styles.retryBtn} onPress={fetchData}>
          <Text style={styles.retryText}>Повторить</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const assignedCount = role.permissions?.length || 0;
  const totalCount = allPermissions.length;

  return (
    <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#0f172a" />
        </TouchableOpacity>
        <Text style={styles.title}>{role.name}</Text>
      </View>

      {/* Описание роли */}
      <View style={styles.card}>
        <Text style={styles.label}>Описание</Text>
        <Text style={styles.value}>{role.description || '-'}</Text>
      </View>

      {/* Статистика */}
      <View style={styles.statsRow}>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>{assignedCount}</Text>
          <Text style={styles.statLabel}>Назначено</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>{totalCount}</Text>
          <Text style={styles.statLabel}>Всего разрешений</Text>
        </View>
      </View>

      {/* Список всех разрешений с чекбоксами */}
      <View style={styles.card}>
        <Text style={styles.label}>Разрешения</Text>
        
        {allPermissions.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="lock-closed-outline" size={32} color="#94a3b8" />
            <Text style={styles.emptyText}>Нет доступных разрешений</Text>
          </View>
        ) : (
          <View style={styles.permissionsList}>
            {allPermissions.map(perm => {
              const isEnabled = hasPermission(perm);
              return (
                <TouchableOpacity
                  key={perm.oid || perm.code}
                  style={[styles.permItem, isEnabled && styles.permItemActive]}
                  onPress={() => togglePermission(perm)}
                  disabled={actionLoading}
                  activeOpacity={0.7}
                >
                  <View style={styles.permInfo}>
                    <Text style={[styles.permCode, isEnabled && styles.permCodeActive]}>
                      {perm.code}
                    </Text>
                    <Text style={styles.permDesc}>{perm.description}</Text>
                  </View>
                  
                  <View style={styles.checkboxContainer}>
                    <View style={[styles.checkbox, isEnabled && styles.checkboxChecked]}>
                      {isEnabled && <Ionicons name="checkmark" size={16} color="#fff" />}
                    </View>
                  </View>
                </TouchableOpacity>
              );
            })}
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: '#f8fafc', padding: 20, paddingBottom: 40 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc', padding: 20 },
  loadingText: { marginTop: 12, fontSize: 15, color: '#64748b' },
  errorText: { fontSize: 16, color: '#dc2626', textAlign: 'center', marginBottom: 20 },
  retryBtn: { backgroundColor: '#2563eb', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 },
  retryText: { color: '#fff', fontWeight: '600', fontSize: 15 },
  
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  backBtn: { padding: 8, marginRight: 12, borderRadius: 8, backgroundColor: '#fff', borderWidth: 1, borderColor: '#e2e8f0' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a', flex: 1 },
  
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 16, marginBottom: 16, borderWidth: 1, borderColor: '#e2e8f0' },
  label: { fontSize: 13, fontWeight: '600', color: '#64748b', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 },
  value: { fontSize: 15, color: '#0f172a' },
  
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  statBox: { flex: 1, backgroundColor: '#fff', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#e2e8f0', alignItems: 'center' },
  statNumber: { fontSize: 24, fontWeight: '700', color: '#2563eb' },
  statLabel: { fontSize: 12, color: '#64748b', marginTop: 4 },
  
  permissionsList: { gap: 8 },
  permItem: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: 12, 
    borderRadius: 10, 
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  permItemActive: { 
    backgroundColor: '#eff6ff',
    borderColor: '#bfdbfe',
  },
  permInfo: { flex: 1, marginRight: 12 },
  permCode: { fontSize: 14, fontWeight: '600', color: '#475569', fontFamily: 'monospace', marginBottom: 2 },
  permCodeActive: { color: '#1e40af' },
  permDesc: { fontSize: 12, color: '#94a3b8' },
  
  checkboxContainer: { 
    width: 24, 
    height: 24, 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#cbd5e1',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  checkboxChecked: {
    backgroundColor: '#2563eb',
    borderColor: '#2563eb',
  },
  
  emptyState: { 
    alignItems: 'center', 
    padding: 32,
    backgroundColor: '#f8fafc',
    borderRadius: 10,
    borderStyle: 'dashed',
    borderWidth: 1,
    borderColor: '#cbd5e1'
  },
  emptyText: { marginTop: 12, fontSize: 14, color: '#94a3b8', textAlign: 'center' }
});