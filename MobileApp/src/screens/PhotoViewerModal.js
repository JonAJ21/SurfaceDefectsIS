// MobileApp/src/screens/PhotoViewerModal.js
import React, { useState, useRef } from 'react';
import {
  Modal, View, Text, StyleSheet, TouchableOpacity, 
  Dimensions, ScrollView, Platform, Image
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { getPhotoUrl } from '../utils/urlHelper';

const { width, height } = Dimensions.get('window');

export default function PhotoViewerModal({ visible, photos, initialIndex, onClose }) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex || 0);
  const scrollViewRef = useRef(null);

  const handleScroll = (event) => {
    const index = Math.round(event.nativeEvent.contentOffset.x / width);
    setCurrentIndex(index);
  };

  const goToNext = () => {
    if (currentIndex < photos.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      scrollViewRef.current?.scrollTo({ x: newIndex * width, animated: true });
    }
  };

  const goToPrev = () => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      setCurrentIndex(newIndex);
      scrollViewRef.current?.scrollTo({ x: newIndex * width, animated: true });
    }
  };

  if (!photos || photos.length === 0) return null;

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="fade"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={28} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.counter}>
            {currentIndex + 1} / {photos.length}
          </Text>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView
          ref={scrollViewRef}
          horizontal
          pagingEnabled
          showsHorizontalScrollIndicator={false}
          onMomentumScrollEnd={handleScroll}
          style={styles.scrollView}
        >
          {photos.map((photo, index) => (
            <View key={index} style={styles.photoContainer}>
              <Image
                source={{ uri: getPhotoUrl(photo) }}
                style={styles.photo}
                resizeMode="contain"
              />
            </View>
          ))}
        </ScrollView>

        {photos.length > 1 && (
          <View style={styles.navigation}>
            <TouchableOpacity 
              style={[styles.navButton, currentIndex === 0 && styles.navButtonDisabled]} 
              onPress={goToPrev}
              disabled={currentIndex === 0}
            >
              <Ionicons name="chevron-back" size={30} color={currentIndex === 0 ? '#666' : '#fff'} />
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.navButton, currentIndex === photos.length - 1 && styles.navButtonDisabled]} 
              onPress={goToNext}
              disabled={currentIndex === photos.length - 1}
            >
              <Ionicons name="chevron-forward" size={30} color={currentIndex === photos.length - 1 ? '#666' : '#fff'} />
            </TouchableOpacity>
          </View>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: Platform.OS === 'ios' ? 50 : 40,
    paddingHorizontal: 20,
    paddingBottom: 20,
    backgroundColor: 'rgba(0,0,0,0.5)',
    zIndex: 10,
  },
  closeButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  counter: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  photoContainer: {
    width: width,
    height: height,
    justifyContent: 'center',
    alignItems: 'center',
  },
  photo: {
    width: width,
    height: height,
  },
  navigation: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingBottom: 40,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  navButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  navButtonDisabled: {
    opacity: 0.5,
  },
});