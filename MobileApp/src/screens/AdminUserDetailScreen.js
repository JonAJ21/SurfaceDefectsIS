import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Switch, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authApi } from '../config/api';

export default function AdminUserDetailScreen({ route, navigation }) {
  const { userIdentifier } = route.params; // Уже в формате oid_xxx
  const [user, setUser] = useState(null);
  const [allRoles, setAllRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      // 🔹 GET с префиксом
      const userRes = await authApi.get(`/v1/users/${userIdentifier}`, { params: { load_roles: true } });
      setUser(userRes.data);

      const rolesRes = await authApi.get('/v1/roles', { params: { limit: 50 } });
      setAllRoles(rolesRes.data.roles || rolesRes.data || []);
    } catch (e) {
      console.error('Fetch error:', e);
      Alert.alert('Ошибка', 'Не удалось загрузить данные');
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const toggleStatus = async () => {
    if (!user || actionLoading) return;
    setActionLoading(true);
    try {
      // 🔹 PATCH activate/deactivate с префиксом
      const endpoint = user.is_active 
        ? `/v1/users/${userIdentifier}/deactivate`
        : `/v1/users/${userIdentifier}/activate`;
      
      await authApi.patch(endpoint);
      await fetchData();
    } catch (e) {
      console.error('Status toggle error:', e);
      Alert.alert('Ошибка', e.response?.data?.detail || 'Не удалось изменить статус');
    } finally { setActionLoading(false); }
  };

  const hasRole = (role) => user?.roles?.some(r => r.oid === role.oid);

  const toggleRole = async (role) => {
    if (actionLoading) return;
    const isAssigned = hasRole(role);
    setActionLoading(true);
    
    try {
      // 🔹 POST/DELETE roles с префиксами для user и role
      const roleIdentifier = role.oid ? `oid_${role.oid}` : `name_${role.name}`;
      const url = `/v1/users/${userIdentifier}/roles/${roleIdentifier}`;
      
      if (isAssigned) await authApi.delete(url);
      else await authApi.post(url);
      
      await fetchData();
    } catch (e) {
      console.error('Role toggle error:', e);
      Alert.alert('Ошибка', e.response?.data?.detail || 'Не удалось изменить роли');
    } finally { setActionLoading(false); }
  };

  if (loading || !user) return <View style={styles.center}><ActivityIndicator size="large" color="#2563eb" /></View>;

  return (
    <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color="#0f172a" /></TouchableOpacity>
        <Text style={styles.title}>Управление</Text>
      </View>

      <View style={styles.card}>
        <View style={styles.avatarRow}>
          <View style={styles.avatarLarge}><Text style={styles.avatarText}>{user.email?.[0]?.toUpperCase()}</Text></View>
          <View style={styles.infoRow}>
            <Text style={styles.email}>{user.email}</Text>
            <Text style={styles.oid}>ID: {user.oid}</Text>
          </View>
        </View>
        
        <View style={styles.divider} />
        
        <View style={styles.switchRow}>
          <Text style={styles.switchLabel}>Статус аккаунта</Text>
          <View style={styles.switchContainer}>
            <Text style={[styles.statusText, user.is_active ? styles.textActive : styles.textInactive]}>
              {user.is_active ? 'Активен' : 'Заблокирован'}
            </Text>
            <Switch 
              value={user.is_active} 
              onValueChange={toggleStatus} 
              disabled={actionLoading}
              trackColor={{ false: '#fee2e2', true: '#86efac' }}
              thumbColor={user.is_active ? '#166534' : '#f4f4f5'}
            />
          </View>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Роли ({user.roles?.length || 0} назначено)</Text>
      <View style={styles.card}>
        {allRoles.length === 0 ? (
          <Text style={styles.empty}>Нет доступных ролей в системе</Text>
        ) : (
          allRoles.map(role => {
            const isEnabled = hasRole(role);
            return (
              <TouchableOpacity
                key={role.oid}
                style={[styles.roleItem, isEnabled && styles.roleItemActive]}
                onPress={() => toggleRole(role)}
                disabled={actionLoading}
                activeOpacity={0.7}
              >
                <View style={styles.roleInfo}>
                  <Text style={[styles.roleName, isEnabled && styles.roleNameActive]}>{role.name}</Text>
                  <Text style={styles.roleDesc}>{role.description}</Text>
                </View>
                <View style={styles.checkboxContainer}>
                  <View style={[styles.checkbox, isEnabled && styles.checkboxChecked]}>
                    {isEnabled && <Ionicons name="checkmark" size={14} color="#fff" />}
                  </View>
                </View>
              </TouchableOpacity>
            );
          })
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: '#f8fafc', padding: 20, paddingBottom: 40 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' },
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  backBtn: { padding: 8, marginRight: 12, borderRadius: 8, backgroundColor: '#fff', borderWidth: 1, borderColor: '#e2e8f0' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 16, marginBottom: 16, borderWidth: 1, borderColor: '#e2e8f0' },
  avatarRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  avatarLarge: { width: 56, height: 56, borderRadius: 28, backgroundColor: '#eff6ff', justifyContent: 'center', alignItems: 'center', marginRight: 16 },
  avatarText: { fontSize: 24, fontWeight: '700', color: '#2563eb' },
  email: { fontSize: 16, fontWeight: '600', color: '#0f172a' },
  oid: { fontSize: 12, color: '#94a3b8', fontFamily: 'monospace', marginTop: 4 },
  divider: { height: 1, backgroundColor: '#f1f5f9', marginVertical: 16 },
  switchRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  switchLabel: { fontSize: 15, fontWeight: '500', color: '#475569' },
  switchContainer: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  statusText: { fontSize: 14, fontWeight: '600' },
  textActive: { color: '#166534' },
  textInactive: { color: '#dc2626' },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#334155', marginBottom: 12, marginLeft: 4 },
  roleItem: { flexDirection: 'row', alignItems: 'center', padding: 12, borderRadius: 10, backgroundColor: '#f8fafc', borderWidth: 1, borderColor: '#e2e8f0', marginBottom: 8 },
  roleItemActive: { backgroundColor: '#eff6ff', borderColor: '#bfdbfe' },
  roleInfo: { flex: 1, marginRight: 12 },
  roleName: { fontSize: 14, fontWeight: '600', color: '#475569' },
  roleNameActive: { color: '#1e40af' },
  roleDesc: { fontSize: 12, color: '#94a3b8', marginTop: 2 },
  checkboxContainer: { width: 20, height: 20, justifyContent: 'center', alignItems: 'center' },
  checkbox: { width: 18, height: 18, borderRadius: 5, borderWidth: 2, borderColor: '#cbd5e1', justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' },
  checkboxChecked: { backgroundColor: '#2563eb', borderColor: '#2563eb' },
  empty: { textAlign: 'center', color: '#94a3b8', padding: 20 }
});