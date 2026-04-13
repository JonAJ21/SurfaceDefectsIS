import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';

export default function AdminDashboardScreen({ navigation }) {
  const { user, isAdmin } = useAuth();

  if (!isAdmin) {
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
    { 
      icon: 'people-outline', 
      title: 'Пользователи', 
      desc: 'Управление доступом и ролями', 
      color: '#3b82f6', 
      screen: 'AdminUsers' 
    },
    { 
      icon: 'shield-checkmark-outline', 
      title: 'Роли', 
      desc: 'Создание и настройка ролей', 
      color: '#8b5cf6', 
      screen: 'AdminRoles' 
    },
    { 
      icon: 'key-outline', 
      title: 'Разрешения', 
      desc: 'Управление кодами доступа', 
      color: '#f59e0b', 
      screen: 'AdminPermissions' 
    },
  ];


  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color="#0f172a" /></TouchableOpacity>
        <Text style={styles.title}>⚙️ Админ-панель</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.welcome}>Привет, {user?.email}</Text>
        <Text style={styles.desc}>Управление доступом к системе.</Text>
      </View>

      <Text style={styles.sectionTitle}>Управление RBAC</Text>
      <View style={styles.grid}>
        {menuItems.map((item) => (
          <TouchableOpacity 
            key={item.title} 
            style={[styles.menuCard, { borderTopColor: item.color }]} 
            onPress={() => navigation.navigate(item.screen)}
          >
            <View style={[styles.iconBox, { backgroundColor: `${item.color}15` }]}>
              <Ionicons name={item.icon} size={28} color={item.color} />
            </View>
            <Text style={styles.menuTitle}>{item.title}</Text>
            <Text style={styles.menuDesc}>{item.desc}</Text>
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
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 20, borderWidth: 1, borderColor: '#e2e8f0' },
  welcome: { fontSize: 16, fontWeight: '600', color: '#0f172a', marginBottom: 4 },
  desc: { fontSize: 13, color: '#64748b' },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#334155', marginBottom: 12 },
  grid: { gap: 16 },
  menuCard: { backgroundColor: '#fff', padding: 16, borderRadius: 14, borderWidth: 1, borderColor: '#e2e8f0', borderTopWidth: 4 },
  iconBox: { width: 44, height: 44, borderRadius: 10, justifyContent: 'center', alignItems: 'center', marginBottom: 10 },
  menuTitle: { fontSize: 15, fontWeight: '600', color: '#0f172a', marginBottom: 4 },
  menuDesc: { fontSize: 12, color: '#64748b' },
  error: { fontSize: 16, color: '#dc2626', textAlign: 'center', marginTop: 100, marginBottom: 20 },
  button: { backgroundColor: '#2563eb', padding: 14, borderRadius: 10, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '600' }
});