import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';

export default function ModeratorDashboardScreen({ navigation }) {
  const { user, isModerator } = useAuth();

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

  const menuItems = [
    { icon: 'location-outline', title: 'Новые дефекты', desc: 'Проверка заявок от пользователей', color: '#f59e0b', count: 3 },
    { icon: 'checkmark-circle-outline', title: 'Верифицированные', desc: 'Одобренные дефекты на карте', color: '#10b981', count: 12 },
    { icon: 'close-circle-outline', title: 'Отклонённые', desc: 'Отклонённые заявки', color: '#ef4444', count: 1 },
  ];

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color="#0f172a" /></TouchableOpacity>
        <Text style={styles.title}>🔍 Модерация</Text>
      </View>

      <View style={styles.statsRow}>
        {menuItems.map(item => (
          <View key={item.title} style={styles.statCard}>
            <Text style={styles.statCount}>{item.count}</Text>
            <Text style={styles.statLabel}>{item.title}</Text>
          </View>
        ))}
      </View>

      <Text style={styles.sectionTitle}>Действия</Text>
      <View style={styles.actionList}>
        {menuItems.map(item => (
          <TouchableOpacity key={item.title} style={styles.actionItem}>
            <Ionicons name={item.icon} size={24} color={item.color} />
            <View style={styles.actionInfo}>
              <Text style={styles.actionTitle}>{item.title}</Text>
              <Text style={styles.actionDesc}>{item.desc}</Text>
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
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  backBtn: { padding: 8, marginRight: 12, borderRadius: 8, backgroundColor: '#fff', borderWidth: 1, borderColor: '#e2e8f0' },
  title: { fontSize: 24, fontWeight: '700', color: '#0f172a' },
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 24 },
  statCard: { flex: 1, backgroundColor: '#fff', padding: 12, borderRadius: 12, borderWidth: 1, borderColor: '#e2e8f0', alignItems: 'center' },
  statCount: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  statLabel: { fontSize: 11, color: '#64748b', marginTop: 4 },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#334155', marginBottom: 12 },
  actionList: { gap: 12 },
  actionItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', padding: 14, borderRadius: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  actionInfo: { flex: 1, marginLeft: 12 },
  actionTitle: { fontSize: 15, fontWeight: '600', color: '#0f172a' },
  actionDesc: { fontSize: 12, color: '#64748b' },
  error: { fontSize: 16, color: '#dc2626', textAlign: 'center', marginTop: 100, marginBottom: 20 },
  button: { backgroundColor: '#2563eb', padding: 14, borderRadius: 10, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '600' }
});