import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';

export default function LoginModal({ navigation }) {
  const { login, loading, apiError, successMessage } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) return;
    try {
      await login({ username, password });
      navigation.goBack();
    } catch {}
  };

  return (
    <View style={styles.backdrop}>
      <TouchableOpacity style={styles.backdropTouchable} activeOpacity={1} onPress={() => navigation.goBack()} />
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
        <View style={styles.modalCard}>
          <View style={styles.header}>
            <Text style={styles.title}>Вход</Text>
            <TouchableOpacity onPress={() => navigation.goBack()} style={styles.closeBtn}><Ionicons name="close" size={24} color="#64748b" /></TouchableOpacity>
          </View>
          {successMessage && <View style={styles.successBox}><Text style={styles.successText}>{successMessage}</Text></View>}
          {apiError && <View style={styles.errorBox}><Text style={styles.errorText}>{apiError}</Text></View>}
          <TextInput style={styles.input} placeholder="Email" value={username} onChangeText={setUsername} autoCapitalize="none" keyboardType="email-address" />
          <View style={styles.passwordWrapper}>
            <TextInput style={styles.passwordInput} placeholder="Пароль" value={password} onChangeText={setPassword} secureTextEntry={!showPassword} autoCapitalize="none" />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeButton}><Ionicons name={showPassword ? 'eye-off' : 'eye'} size={22} color="#64748b" /></TouchableOpacity>
          </View>
          <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Войти</Text>}
          </TouchableOpacity>
          <TouchableOpacity onPress={() => navigation.replace('Register')} style={styles.linkContainer}><Text style={styles.linkText}>Нет аккаунта? Зарегистрироваться</Text></TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: 'transparent', justifyContent: 'center', alignItems: 'center' },
  backdropTouchable: { ...StyleSheet.absoluteFillObject },
  container: { width: '90%', maxWidth: 480, paddingHorizontal: 16 },
  modalCard: { backgroundColor: '#fff', borderRadius: 20, padding: 24, elevation: 5, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.15, shadowRadius: 10 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  title: { fontSize: 24, fontWeight: '700', color: '#0f172a' },
  closeBtn: { padding: 4 },
  input: { backgroundColor: '#f8fafc', padding: 14, borderRadius: 10, marginBottom: 12, borderWidth: 1, borderColor: '#e2e8f0' },
  passwordWrapper: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f8fafc', borderRadius: 10, borderWidth: 1, borderColor: '#e2e8f0', marginBottom: 16 },
  passwordInput: { flex: 1, padding: 14 },
  eyeButton: { padding: 12 },
  successBox: { backgroundColor: '#f0fdf4', padding: 10, borderRadius: 8, marginBottom: 12, borderWidth: 1, borderColor: '#bbf7d0' },
  successText: { color: '#166534', textAlign: 'center', fontSize: 13 },
  errorBox: { backgroundColor: '#fef2f2', padding: 10, borderRadius: 8, marginBottom: 12, borderWidth: 1, borderColor: '#fecaca' },
  errorText: { color: '#dc2626', textAlign: 'center', fontSize: 13 },
  button: { backgroundColor: '#2563eb', padding: 14, borderRadius: 10, alignItems: 'center', marginTop: 4 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  linkContainer: { marginTop: 16, alignItems: 'center' },
  linkText: { color: '#2563eb', fontSize: 14, fontWeight: '500' }
});