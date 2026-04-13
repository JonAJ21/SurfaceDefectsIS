import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authApi } from '../config/api';

const PAGE_SIZE = 20;

export default function AdminUsersScreen({ navigation }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchUsers = async (currentOffset) => {
    setLoading(true);
    try {
      const { data } = await authApi.get('/v1/users', {
        params: { offset: currentOffset, limit: PAGE_SIZE }
      });
      const list = data.users || data || [];
      setUsers(list);
      // Если вернули меньше, чем размер страницы → это последняя страница
      setHasMore(list.length === PAGE_SIZE);
    } catch (e) {
      console.error('Fetch users error:', e);
    } finally {
      setLoading(false);
    }
  };

  // Сброс на первую страницу при изменении поиска
  useEffect(() => {
    setOffset(0);
  }, [searchQuery]);

  // Загрузка данных при изменении offset
  useEffect(() => {
    fetchUsers(offset);
  }, [offset]);

  const filteredUsers = users.filter(u =>
    u.email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleNext = () => {
    if (hasMore && !loading) setOffset(prev => prev + PAGE_SIZE);
  };

  const handlePrev = () => {
    if (offset > 0 && !loading) setOffset(prev => Math.max(0, prev - PAGE_SIZE));
  };

  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#0f172a" />
        </TouchableOpacity>
        <Text style={styles.title}>Пользователи</Text>
      </View>

      <View style={styles.searchBox}>
        <Ionicons name="search" size={20} color="#94a3b8" />
        <TextInput
          style={styles.searchInput}
          placeholder="Поиск по email..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      {loading && users.length === 0 ? (
        <ActivityIndicator size="large" color="#2563eb" style={{ marginTop: 40 }} />
      ) : (
        <>
          <ScrollView contentContainerStyle={styles.list}>
            {filteredUsers.length === 0 ? (
              <Text style={styles.empty}>Пользователи не найдены</Text>
            ) : (
              filteredUsers.map(user => (
                <TouchableOpacity
                  key={user.oid}
                  style={styles.card}
                  onPress={() => navigation.navigate('AdminUserDetail', { userIdentifier: `oid_${user.oid}` })}
                >
                  <View style={styles.userHeader}>
                    <View style={styles.avatarPlaceholder}>
                      <Text style={styles.avatarText}>{user.email?.[0]?.toUpperCase() || '?'}</Text>
                    </View>
                    <View style={styles.userInfo}>
                      <Text style={styles.userName}>{user.email}</Text>
                      <Text style={[styles.badge, user.is_active ? styles.badgeActive : styles.badgeInactive]}>
                        {user.is_active ? 'Активен' : 'Неактивен'}
                      </Text>
                    </View>
                    <Ionicons name="chevron-forward" size={20} color="#cbd5e1" />
                  </View>
                </TouchableOpacity>
              ))
            )}
          </ScrollView>

          {/* 🔹 Панель пагинации */}
          <View style={styles.pagination}>
            <TouchableOpacity
              style={[styles.pageBtn, offset === 0 && styles.pageBtnDisabled]}
              onPress={handlePrev}
              disabled={offset === 0 || loading}
            >
              <Ionicons name="chevron-back" size={16} color={offset === 0 ? '#cbd5e1' : '#0f172a'} />
              <Text style={[styles.pageText, offset === 0 && styles.pageTextDisabled]}>Назад</Text>
            </TouchableOpacity>

            <View style={styles.pageIndicatorBox}>
              <Text style={styles.pageIndicator}>Стр. {currentPage}</Text>
            </View>

            <TouchableOpacity
              style={[styles.pageBtn, !hasMore && styles.pageBtnDisabled]}
              onPress={handleNext}
              disabled={!hasMore || loading}
            >
              <Text style={[styles.pageText, !hasMore && styles.pageTextDisabled]}>Вперёд</Text>
              <Ionicons name="chevron-forward" size={16} color={!hasMore ? '#cbd5e1' : '#0f172a'} />
            </TouchableOpacity>
          </View>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  header: { flexDirection: 'row', alignItems: 'center', padding: 20, paddingBottom: 10 },
  backBtn: { padding: 8, backgroundColor: '#fff', borderRadius: 8, borderWidth: 1, borderColor: '#e2e8f0', marginRight: 12 },
  title: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  searchBox: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 10, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e2e8f0', marginHorizontal: 20, marginBottom: 16 },
  searchInput: { flex: 1, padding: 12, fontSize: 15 },
  list: { paddingHorizontal: 20, paddingBottom: 20 },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  userHeader: { flexDirection: 'row', alignItems: 'center' },
  avatarPlaceholder: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#eff6ff', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  avatarText: { fontSize: 18, fontWeight: '600', color: '#2563eb' },
  userInfo: { flex: 1 },
  userName: { fontSize: 15, fontWeight: '600', color: '#0f172a', marginBottom: 4 },
  badge: { fontSize: 12, fontWeight: '500', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 12, alignSelf: 'flex-start' },
  badgeActive: { backgroundColor: '#f0fdf4', color: '#166534' },
  badgeInactive: { backgroundColor: '#fef2f2', color: '#dc2626' },
  empty: { textAlign: 'center', color: '#94a3b8', marginTop: 40 },
  
  // 🔹 Стили пагинации
  pagination: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderTopWidth: 1, borderTopColor: '#e2e8f0', backgroundColor: '#fff' },
  pageBtn: { flexDirection: 'row', alignItems: 'center', paddingVertical: 8, paddingHorizontal: 12, borderRadius: 8 },
  pageBtnDisabled: { opacity: 0.5 },
  pageText: { fontSize: 14, fontWeight: '600', color: '#0f172a', marginHorizontal: 4 },
  pageTextDisabled: { color: '#94a3b8' },
  pageIndicatorBox: { backgroundColor: '#f1f5f9', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  pageIndicator: { fontSize: 13, fontWeight: '600', color: '#475569' }
});