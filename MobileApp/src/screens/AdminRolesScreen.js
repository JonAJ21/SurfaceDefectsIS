import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput, Alert, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authApi } from '../config/api';

const getRoleIdentifier = (role) => role.oid ? `oid_${role.oid}` : `name_${role.name}`;

export default function AdminRolesScreen({ navigation }) {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newRoleName, setNewRoleName] = useState('');
  const [newRoleDesc, setNewRoleDesc] = useState('');

  const fetchRoles = async () => {
    setLoading(true);
    try {
      const { data } = await authApi.get('/v1/roles', { params: { limit: 50 } });
      setRoles(Array.isArray(data) ? data : (data.roles || data.data?.roles || []));
    } catch (e) {
      Alert.alert('Ошибка', e.response?.data?.detail || 'Не удалось загрузить роли');
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchRoles(); }, []);

  const handleCreate = async () => {
    if (!newRoleName.trim()) return Alert.alert('Ошибка', 'Введите имя роли');
    try {
      await authApi.post('/v1/roles/create', { name: newRoleName, description: newRoleDesc });
      setShowCreateModal(false); setNewRoleName(''); setNewRoleDesc('');
      fetchRoles();
      Alert.alert('Успех', 'Роль создана');
    } catch (e) {
      Alert.alert('Ошибка', e.response?.data?.detail || 'Не удалось создать');
    }
  };

  const handleDelete = async (role) => {
    const identifier = getRoleIdentifier(role);
    Alert.alert('Удаление роли', `Удалить ${role.name}?`, [
      { text: 'Отмена', style: 'cancel' },
      { text: 'Удалить', style: 'destructive', onPress: async () => {
          try {
            await authApi.delete(`/v1/roles/${encodeURIComponent(identifier)}`);
            fetchRoles();
            Alert.alert('Успех', 'Роль удалена');
          } catch (e) {
            Alert.alert('Ошибка', e.response?.data?.detail || 'Не удалось удалить');
          }
        }
      }
    ]);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color="#0f172a" /></TouchableOpacity>
        <Text style={styles.title}>Управление ролями</Text>
        <TouchableOpacity onPress={() => setShowCreateModal(!showCreateModal)} style={styles.addButton}>
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {showCreateModal && (
        <View style={styles.createForm}>
          <TextInput style={styles.input} placeholder="Имя роли" value={newRoleName} onChangeText={setNewRoleName} />
          <TextInput style={styles.input} placeholder="Описание" value={newRoleDesc} onChangeText={setNewRoleDesc} />
          <TouchableOpacity style={styles.submitBtn} onPress={handleCreate}><Text style={styles.submitText}>Создать</Text></TouchableOpacity>
        </View>
      )}

      {loading ? <ActivityIndicator size="large" color="#2563eb" style={{ marginTop: 20 }} /> : (
        <ScrollView contentContainerStyle={styles.list}>
          {roles.length === 0 ? <Text style={styles.empty}>Нет ролей</Text> : (
            roles.map(role => (
              <TouchableOpacity key={role.oid || role.name} style={styles.card} onPress={() => navigation.navigate('RoleDetail', { roleIdentifier: getRoleIdentifier(role) })}>
                <View style={styles.cardHeader}>
                  <Text style={styles.roleName}>{role.name}</Text>
                  <TouchableOpacity onPress={(e) => { e.stopPropagation(); handleDelete(role); }}>
                    <Ionicons name="trash-outline" size={20} color="#ef4444" />
                  </TouchableOpacity>
                </View>
                <Text style={styles.roleDesc}>{role.description}</Text>
              </TouchableOpacity>
            ))
          )}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc', padding: 20 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 },
  backBtn: { padding: 8, backgroundColor: '#fff', borderRadius: 8, borderWidth: 1, borderColor: '#e2e8f0' },
  title: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  addButton: { backgroundColor: '#2563eb', width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  createForm: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 20, borderWidth: 1, borderColor: '#e2e8f0' },
  input: { backgroundColor: '#f8fafc', padding: 12, borderRadius: 8, marginBottom: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  submitBtn: { backgroundColor: '#10b981', padding: 12, borderRadius: 8, alignItems: 'center' },
  submitText: { color: '#fff', fontWeight: '600' },
  list: { paddingBottom: 40 },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }, // Убрал gap и marginBottom
  roleName: { fontSize: 16, fontWeight: '600', color: '#0f172a' },
  roleDesc: { fontSize: 13, color: '#64748b', marginTop: 4 },
  empty: { textAlign: 'center', color: '#94a3b8', marginTop: 40 }
});