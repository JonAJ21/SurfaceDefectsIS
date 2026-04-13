import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function CreateDefectScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Создание дефекта</Text>
      <Text style={styles.subtitle}>Экран в разработке 🚧</Text>
      <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
        <Text style={styles.buttonText}>Назад</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' },
  title: { fontSize: 22, fontWeight: '700', marginBottom: 12 },
  subtitle: { fontSize: 14, color: '#64748b', marginBottom: 30 },
  button: { backgroundColor: '#2563eb', padding: 14, borderRadius: 10, width: '100%', alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '600' }
});