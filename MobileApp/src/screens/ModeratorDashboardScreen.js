// MobileApp/src/screens/ModeratorDashboardScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, RefreshControl, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { defectsApi } from '../config/api';
import { getPendingDefects } from '../services/defectsService';

export default function ModeratorDashboardScreen({ navigation }) {
  const { user, isModerator } = useAuth();
  const [stats, setStats] = useState({
    pending: 0,
    approved: 0,
    rejected: 0,
    fixed: 0,
    total: 0
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    if (!isModerator) return;
    
    try {
      const pendingData = await getPendingDefects({ limit: 100, offset: 0 });
      const pendingCount = pendingData.length;
      
      const allResponse = await defectsApi.get('/v1/defects', { params: { limit: 100, offset: 0 } });
      const allDefects = allResponse.data || [];
      
      const approvedCount = allDefects.filter(d => d.status === 'approved').length;
      const rejectedCount = allDefects.filter(d => d.status === 'rejected').length;
      const fixedCount = allDefects.filter(d => d.status === 'fixed').length;
      
      setStats({
        pending: pendingCount,
        approved: approvedCount,
        rejected: rejectedCount,
        fixed: fixedCount,
        total: allDefects.length
      });
    } catch (error) {
      console.error('Fetch stats error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (isModerator) {
      fetchStats();
    }
  }, [isModerator]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchStats();
  };

  if (!isModerator) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>🚫 Доступ запрещён</Text>
        <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
          <Text style={styles.buttonText}>Назад в профиль</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  const menuItems = [
    { 
      icon: 'time-outline', 
      title: 'На модерации', 
      desc: 'Дефекты, ожидающие проверки', 
      color: '#f59e0b', 
      count: stats.pending,
      screen: 'ModeratorDefects',
      params: { status: 'pending' }
    },
    { 
      icon: 'checkmark-circle-outline', 
      title: 'Подтверждённые', 
      desc: 'Одобренные дефекты', 
      color: '#10b981', 
      count: stats.approved,
      screen: 'ModeratorDefects',
      params: { status: 'approved' }
    },
    { 
      icon: 'close-circle-outline', 
      title: 'Отклонённые', 
      desc: 'Отклонённые заявки', 
      color: '#ef4444', 
      count: stats.rejected,
      screen: 'ModeratorDefects',
      params: { status: 'rejected' }
    },
    { 
      icon: 'checkmark-done-circle-outline', 
      title: 'Исправленные', 
      desc: 'Отмеченные как исправленные', 
      color: '#3b82f6', 
      count: stats.fixed,
      screen: 'ModeratorDefects',
      params: { status: 'fixed' }
    },
    { 
      icon: 'list-outline', 
      title: 'Все дефекты', 
      desc: 'Просмотр всех дефектов', 
      color: '#64748b', 
      count: stats.total,
      screen: 'ModeratorDefects',
      params: { status: 'all' }
    },
  ];

  return (
    <ScrollView 
      contentContainerStyle={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#0f172a" />
        </TouchableOpacity>
        <Text style={styles.title}>🔍 Панель модератора</Text>
      </View>

      <View style={styles.welcomeCard}>
        <Ionicons name="shield-checkmark" size={32} color="#2563eb" />
        <View style={styles.welcomeTextContainer}>
          <Text style={styles.welcomeText}>Здравствуйте, {user?.email?.split('@')[0] || 'Модератор'}</Text>
          <Text style={styles.welcomeSubtext}>Управляйте дефектами и проверяйте заявки</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Статистика</Text>
      <View style={styles.statsGrid}>
        <View style={[styles.statCard, { borderTopColor: '#f59e0b' }]}>
          <Text style={[styles.statCount, { color: '#f59e0b' }]}>{stats.pending}</Text>
          <Text style={styles.statLabel}>На модерации</Text>
        </View>
        <View style={[styles.statCard, { borderTopColor: '#10b981' }]}>
          <Text style={[styles.statCount, { color: '#10b981' }]}>{stats.approved}</Text>
          <Text style={styles.statLabel}>Подтверждены</Text>
        </View>
        <View style={[styles.statCard, { borderTopColor: '#ef4444' }]}>
          <Text style={[styles.statCount, { color: '#ef4444' }]}>{stats.rejected}</Text>
          <Text style={styles.statLabel}>Отклонены</Text>
        </View>
        <View style={[styles.statCard, { borderTopColor: '#3b82f6' }]}>
          <Text style={[styles.statCount, { color: '#3b82f6' }]}>{stats.fixed}</Text>
          <Text style={styles.statLabel}>Исправлены</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Разделы модерации</Text>
      <View style={styles.actionList}>
        {menuItems.map((item) => (
          <TouchableOpacity 
            key={item.title} 
            style={styles.actionItem} 
            onPress={() => navigation.navigate(item.screen, item.params)}
          >
            <View style={[styles.iconContainer, { backgroundColor: item.color + '15' }]}>
              <Ionicons name={item.icon} size={24} color={item.color} />
            </View>
            <View style={styles.actionInfo}>
              <Text style={styles.actionTitle}>{item.title}</Text>
              <Text style={styles.actionDesc}>{item.desc}</Text>
            </View>
            <View style={styles.badge}>
              <Text style={[styles.badgeText, { color: item.color }]}>{item.count}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#94a3b8" />
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: '#f8fafc', padding: 20 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' },
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  backBtn: { padding: 8, marginRight: 12, borderRadius: 8, backgroundColor: '#fff', borderWidth: 1, borderColor: '#e2e8f0' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  
  welcomeCard: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: '#eff6ff', 
    padding: 16, 
    borderRadius: 16, 
    marginBottom: 24,
    gap: 12
  },
  welcomeTextContainer: { flex: 1 },
  welcomeText: { fontSize: 16, fontWeight: '600', color: '#1e40af', marginBottom: 4 },
  welcomeSubtext: { fontSize: 13, color: '#3b82f6' },
  
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#334155', marginBottom: 12, marginTop: 8 },
  
  statsGrid: { 
    flexDirection: 'row', 
    flexWrap: 'wrap', 
    gap: 12, 
    marginBottom: 24 
  },
  statCard: { 
    flex: 1, 
    minWidth: '45%', 
    backgroundColor: '#fff', 
    padding: 16, 
    borderRadius: 12, 
    borderWidth: 1, 
    borderColor: '#e2e8f0', 
    borderTopWidth: 4,
    alignItems: 'center' 
  },
  statCount: { fontSize: 28, fontWeight: '700', marginBottom: 4 },
  statLabel: { fontSize: 12, color: '#64748b' },
  
  actionList: { gap: 12 },
  actionItem: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: '#fff', 
    padding: 14, 
    borderRadius: 12, 
    borderWidth: 1, 
    borderColor: '#e2e8f0',
    gap: 12
  },
  iconContainer: { width: 44, height: 44, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  actionInfo: { flex: 1 },
  actionTitle: { fontSize: 15, fontWeight: '600', color: '#0f172a', marginBottom: 2 },
  actionDesc: { fontSize: 12, color: '#64748b' },
  badge: { backgroundColor: '#f1f5f9', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12 },
  badgeText: { fontSize: 13, fontWeight: '600' },
  
  error: { fontSize: 16, color: '#dc2626', textAlign: 'center', marginTop: 100, marginBottom: 20 },
  button: { backgroundColor: '#2563eb', padding: 14, borderRadius: 10, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '600' }
});