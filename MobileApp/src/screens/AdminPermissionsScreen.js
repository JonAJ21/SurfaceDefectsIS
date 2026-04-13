import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput, Alert, ActivityIndicator, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authApi } from '../config/api';
import { AUTH_SERVICE_URL } from '../config/constants';
import { storage } from '../utils/storage';

export default function AdminPermissionsScreen({ navigation }) {
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPermCode, setNewPermCode] = useState('');
  const [newPermDesc, setNewPermDesc] = useState('');

  const fetchPermissions = async () => {
    setLoading(true);
    try {
      const { data } = await authApi.get('/v1/permissions', { params: { limit: 50 } });
      setPermissions(Array.isArray(data) ? data : (data.permissions || data.data?.permissions || []));
    } catch (e) {
      Alert.alert('Ошибка', e.response?.data?.detail || 'Не удалось загрузить разрешения');
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchPermissions(); }, []);

  const handleCreate = async () => {
    if (!newPermCode.trim()) return Alert.alert('Ошибка', 'Введите код разрешения');
    try {
      await authApi.post('/v1/permission/create', { code: newPermCode, description: newPermDesc });
      setShowCreateModal(false); setNewPermCode(''); setNewPermDesc('');
      fetchPermissions();
      Alert.alert('Успех', 'Разрешение создано');
    } catch (e) {
      Alert.alert('Ошибка', e.response?.data?.detail || 'Не удалось создать');
    }
  };

  const getPermIdentifier = (perm) => perm.oid ? `oid_${perm.oid}` : `code_${perm.code}`;

  const handleDelete = async (perm) => {
    const identifier = getPermIdentifier(perm);
    
    console.log('🗑️ [DELETE] Permission:', perm.code, '| ID:', identifier);
    
    // 🔹 Кроссплатформенное подтверждение
    let confirmed = false;
    
    if (Platform.OS === 'web') {
      // Web: используем window.confirm
      confirmed = window.confirm(`Удалить разрешение "${perm.code}"?\n\nЭто действие необратимо.`);
    } else {
      // Mobile: используем Alert.alert с Promise
      confirmed = await new Promise((resolve) => {
        Alert.alert(
          'Удаление разрешения',
          `Удалить ${perm.code}?`,
          [
            { text: 'Отмена', style: 'cancel', onPress: () => resolve(false) },
            { text: 'Удалить', style: 'destructive', onPress: () => resolve(true) }
          ]
        );
      });
    }
    
    // Если пользователь отменил
    if (!confirmed) {
      console.log('⛔ [DELETE] Cancelled by user');
      return;
    }
    
    console.log('✅ [DELETE] Confirmed. Starting deletion...');
    
    try {
      // 1️⃣ Пробуем через axios
      console.log(' Sending DELETE via axios...');
      await authApi.delete(`/v1/permissions/${identifier}`);
      console.log('✅ Axios DELETE successful');
      
      fetchPermissions();
      Alert.alert('Успех', 'Разрешение удалено');
    } catch (axiosErr) {
      console.error('❌ Axios DELETE failed:', {
        status: axiosErr.response?.status,
        statusText: axiosErr.response?.statusText,
        data: axiosErr.response?.data,
        message: axiosErr.message
      });
      
      // 2️⃣ Fallback на fetch
      try {
        console.log('🔄 Retrying with raw fetch...');
        const token = await storage.getItem('access_token');
        const url = `${AUTH_SERVICE_URL}/v1/permissions/${identifier}`;
        
        console.log('📍 Fetch URL:', url);
        console.log('🔑 Token:', token ? `${token.substring(0, 20)}...` : 'null');
        
        const res = await fetch(url, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        console.log('📥 Fetch response status:', res.status);
        
        if (res.ok) {
          console.log('✅ Fetch DELETE successful');
          fetchPermissions();
          Alert.alert('Успех', 'Разрешение удалено');
        } else {
          const errData = await res.json().catch(() => ({}));
          console.error('❌ Fetch DELETE failed:', res.status, errData);
          Alert.alert(`Ошибка ${res.status}`, errData.detail || 'Не удалось удалить разрешение');
        }
      } catch (fetchErr) {
        console.error('💥 Fetch also failed:', fetchErr);
        Alert.alert('Ошибка сети', fetchErr.message);
      }
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color="#0f172a" /></TouchableOpacity>
        <Text style={styles.title}>Разрешения</Text>
        <TouchableOpacity onPress={() => setShowCreateModal(!showCreateModal)} style={styles.addButton}>
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {showCreateModal && (
        <View style={styles.createForm}>
          <TextInput style={styles.input} placeholder="Код (напр. users.edit)" value={newPermCode} onChangeText={setNewPermCode} />
          <TextInput style={styles.input} placeholder="Описание" value={newPermDesc} onChangeText={setNewPermDesc} />
          <TouchableOpacity style={styles.submitBtn} onPress={handleCreate}><Text style={styles.submitText}>Создать</Text></TouchableOpacity>
        </View>
      )}

      {loading ? <ActivityIndicator size="large" color="#2563eb" style={{ marginTop: 20 }} /> : (
        <ScrollView contentContainerStyle={styles.list}>
          {permissions.length === 0 ? <Text style={styles.empty}>Нет разрешений</Text> : (
            permissions.map(perm => (
              <View key={perm.oid || perm.code} style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.permCode}>{perm.code}</Text>
                  <TouchableOpacity onPress={() => handleDelete(perm)}>
                    <Ionicons name="trash-outline" size={20} color="#ef4444" />
                  </TouchableOpacity>
                </View>
                <Text style={styles.permDesc}>{perm.description}</Text>
              </View>
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
  addButton: { backgroundColor: '#f59e0b', width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  createForm: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 20, borderWidth: 1, borderColor: '#e2e8f0' },
  input: { backgroundColor: '#f8fafc', padding: 12, borderRadius: 8, marginBottom: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  submitBtn: { backgroundColor: '#10b981', padding: 12, borderRadius: 8, alignItems: 'center' },
  submitText: { color: '#fff', fontWeight: '600' },
  list: { paddingBottom: 40 },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  permCode: { fontSize: 16, fontWeight: '600', color: '#b45309', fontFamily: 'monospace' },
  permDesc: { fontSize: 13, color: '#64748b' },
  empty: { textAlign: 'center', color: '#94a3b8', marginTop: 40 }
});