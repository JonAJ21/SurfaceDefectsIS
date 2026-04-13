import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';
import { useAuth } from '../context/AuthContext';

// ===== ГЛАВНЫЕ ЭКРАНЫ =====
import MapScreen from '../screens/MapScreen';
import ProfileScreen from '../screens/ProfileScreen';

// ===== МОДАЛКИ АВТОРИЗАЦИИ =====
import LoginModal from '../screens/LoginModal';
import RegisterModal from '../screens/RegisterModal';

// ===== СОЗДАНИЕ ДЕФЕКТА =====
import CreateDefectScreen from '../screens/CreateDefectScreen';

// ===== АДМИН ПАНЕЛЬ =====
import AdminDashboardScreen from '../screens/AdminDashboardScreen';
import AdminUsersScreen from '../screens/AdminUsersScreen';
import AdminUserDetailScreen from '../screens/AdminUserDetailScreen';
import AdminRolesScreen from '../screens/AdminRolesScreen';
import RoleDetailScreen from '../screens/RoleDetailScreen';
import AdminPermissionsScreen from '../screens/AdminPermissionsScreen';

// ===== МОДЕРАТОР =====
import ModeratorDashboardScreen from '../screens/ModeratorDashboardScreen';
import ModeratorDefectsScreen from '../screens/ModeratorDefectsScreen';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  const { loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' }}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          animation: 'slide_from_right',
        }}
      >
        {/* ===== ГЛАВНЫЙ ЭКРАН - КАРТА ===== */}
        <Stack.Screen name="Map" component={MapScreen} />
        
        {/* ===== МОДАЛКИ С ПРОЗРАЧНЫМ ФОНОМ ===== */}
        <Stack.Screen 
          name="Profile" 
          component={ProfileScreen} 
          options={{ 
            presentation: 'transparentModal',
            animation: 'slide_from_bottom',
            cardStyle: { backgroundColor: 'transparent' }
          }} 
        />
        <Stack.Screen 
          name="Login" 
          component={LoginModal} 
          options={{ 
            presentation: 'transparentModal',
            animation: 'slide_from_bottom',
            cardStyle: { backgroundColor: 'transparent' }
          }} 
        />
        <Stack.Screen 
          name="Register" 
          component={RegisterModal} 
          options={{ 
            presentation: 'transparentModal',
            animation: 'slide_from_bottom',
            cardStyle: { backgroundColor: 'transparent' }
          }} 
        />
        <Stack.Screen 
          name="CreateDefect" 
          component={CreateDefectScreen} 
          options={{ 
            presentation: 'transparentModal',
            animation: 'slide_from_bottom',
            cardStyle: { backgroundColor: 'transparent' }
          }} 
        />
        
        {/* ===== АДМИН ПАНЕЛЬ ===== */}
        <Stack.Screen name="AdminDashboard" component={AdminDashboardScreen} />
        <Stack.Screen name="AdminUsers" component={AdminUsersScreen} />
        <Stack.Screen name="AdminUserDetail" component={AdminUserDetailScreen} />
        <Stack.Screen name="AdminRoles" component={AdminRolesScreen} />
        <Stack.Screen name="RoleDetail" component={RoleDetailScreen} />
        <Stack.Screen name="AdminPermissions" component={AdminPermissionsScreen} />
        
        {/* ===== МОДЕРАТОР ===== */}
        <Stack.Screen name="ModeratorDashboard" component={ModeratorDashboardScreen} />
        <Stack.Screen name="ModeratorDefects" component={ModeratorDefectsScreen} />
        
      </Stack.Navigator>
    </NavigationContainer>
  );
}