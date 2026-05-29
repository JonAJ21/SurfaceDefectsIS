// // MobileApp/src/components/DefectPopup.js
// import React from 'react';
// import {
//   View, Text, StyleSheet, TouchableOpacity, Image,
//   Modal, ScrollView, Dimensions, Platform
// } from 'react-native';
// import { Ionicons } from '@expo/vector-icons';
// import { getPhotoUrl } from '../utils/urlHelper';
// import { DEFECT_TYPE_LABELS, SEVERITY_LABELS } from '../services/defectsService';
// import { formatDate } from '../utils/date';

// const { height } = Dimensions.get('window');

// export default function DefectPopup({ visible, defect, onClose, onNavigate }) {
//   if (!visible || !defect) return null;

//   const hasPhotos = defect.photos && defect.photos.length > 0;
  
//   console.log('📸 DefectPopup - hasPhotos:', hasPhotos);
//   console.log('📸 DefectPopup - photos count:', defect.photos?.length);
//   console.log('📸 DefectPopup - photos:', defect.photos);

//   const severityColor = {
//     low: '#22c55e',
//     medium: '#f59e0b',
//     high: '#f97316',
//     critical: '#dc2626'
//   }[defect.severity] || '#64748b';

//   return (
//     <Modal
//       visible={visible}
//       transparent={true}
//       animationType="slide"
//       onRequestClose={onClose}
//     >
//       <View style={styles.overlay}>
//         <TouchableOpacity style={styles.backdrop} activeOpacity={1} onPress={onClose} />
        
//         <View style={styles.container}>
//           <View style={styles.header}>
//             <View style={[styles.severityBadge, { backgroundColor: severityColor + '20' }]}>
//               <View style={[styles.severityDot, { backgroundColor: severityColor }]} />
//               <Text style={[styles.severityText, { color: severityColor }]}>
//                 {SEVERITY_LABELS[defect.severity] || defect.severity}
//               </Text>
//             </View>
//             <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
//               <Ionicons name="close" size={24} color="#64748b" />
//             </TouchableOpacity>
//           </View>

//           <ScrollView contentContainerStyle={styles.scrollContent}>
//             <Text style={styles.defectType}>
//               {DEFECT_TYPE_LABELS[defect.defect_type] || defect.defect_type}
//             </Text>

//             {defect.description ? (
//               <Text style={styles.description}>{"jdklsjkldjakljdkaljdklaj"}</Text>
//             ) : (
//               <Text style={styles.noDescription}>Нет описания</Text>
//             )}

//             {defect.road_name && defect.road_name !== 'null' && (
//               <View style={styles.infoRow}>
//                 <Ionicons name="location-outline" size={18} color="#64748b" />
//                 <Text style={styles.infoText}>{defect.road_name}</Text>
//               </View>
//             )}

//             <View style={styles.infoRow}>
//               <Ionicons name="time-outline" size={18} color="#64748b" />
//               <Text style={styles.infoText}>{formatDate(defect.created_at)}</Text>
//             </View>

//             {/* ========== БЛОК ФОТОГРАФИЙ ========== */}
//             <View style={styles.photosBlock}>
//               <Text style={styles.photosTitle}>
//                 📸 Фотографии {hasPhotos ? `(${defect.photos.length})` : ''}
//               </Text>
              
//               {hasPhotos ? (
//                 defect.photos.map((photo, index) => (
//                   <TouchableOpacity 
//                     key={index} 
//                     style={styles.photoWrapper}
//                     onPress={() => {
//                       // Открываем фото в браузере или показываем alert с URL
//                       alert(`Фото ${index + 1}:\n${getPhotoUrl(photo)}`);
//                     }}
//                   >
//                     <Image 
//                       source={{ uri: getPhotoUrl(photo) }} 
//                       style={styles.photo}
//                       resizeMode="cover"
//                       onError={(e) => console.log(`❌ Ошибка фото ${index}:`, e.nativeEvent.error)}
//                       onLoad={() => console.log(`✅ Фото ${index} загружено`)}
//                     />
//                     <Text style={styles.photoUrl} numberOfLines={1}>
//                       {getPhotoUrl(photo)}
//                     </Text>
//                   </TouchableOpacity>
//                 ))
//               ) : (
//                 <View style={styles.noPhotos}>
//                   <Ionicons name="camera-outline" size={32} color="#cbd5e1" />
//                   <Text style={styles.noPhotosText}>Нет фотографий</Text>
//                 </View>
//               )}
//             </View>

//             {defect.lat && defect.lon && (
//               <TouchableOpacity 
//                 style={styles.navigateBtn}
//                 onPress={() => {
//                   onClose();
//                   onNavigate(defect.lat, defect.lon);
//                 }}
//               >
//                 <Ionicons name="navigate" size={20} color="#fff" />
//                 <Text style={styles.navigateBtnText}>Показать на карте</Text>
//               </TouchableOpacity>
//             )}
//           </ScrollView>
//         </View>
//       </View>
//     </Modal>
//   );
// }

// const styles = StyleSheet.create({
//   overlay: {
//     flex: 1,
//     justifyContent: 'flex-end',
//   },
//   backdrop: {
//     ...StyleSheet.absoluteFillObject,
//     backgroundColor: 'rgba(0,0,0,0.5)',
//   },
//   container: {
//     backgroundColor: '#fff',
//     borderTopLeftRadius: 20,
//     borderTopRightRadius: 20,
//     maxHeight: height * 0.85,
//   },
//   scrollContent: {
//     padding: 20,
//     paddingBottom: 30,
//   },
//   header: {
//     flexDirection: 'row',
//     justifyContent: 'space-between',
//     alignItems: 'center',
//     padding: 20,
//     paddingBottom: 10,
//     borderBottomWidth: 1,
//     borderBottomColor: '#f1f5f9',
//   },
//   severityBadge: {
//     flexDirection: 'row',
//     alignItems: 'center',
//     paddingHorizontal: 10,
//     paddingVertical: 5,
//     borderRadius: 20,
//     gap: 6,
//   },
//   severityDot: {
//     width: 8,
//     height: 8,
//     borderRadius: 4,
//   },
//   severityText: {
//     fontSize: 12,
//     fontWeight: '600',
//   },
//   closeBtn: {
//     padding: 4,
//   },
//   defectType: {
//     fontSize: 20,
//     fontWeight: '700',
//     color: '#0f172a',
//     marginBottom: 12,
//   },
//   description: {
//     fontSize: 15,
//     color: '#475569',
//     lineHeight: 22,
//     marginBottom: 16,
//   },
//   noDescription: {
//     fontSize: 14,
//     color: '#94a3b8',
//     fontStyle: 'italic',
//     marginBottom: 16,
//   },
//   infoRow: {
//     flexDirection: 'row',
//     alignItems: 'center',
//     gap: 10,
//     marginBottom: 12,
//   },
//   infoText: {
//     flex: 1,
//     fontSize: 14,
//     color: '#64748b',
//   },
//   photosBlock: {
//     marginTop: 16,
//     marginBottom: 16,
//   },
//   photosTitle: {
//     fontSize: 16,
//     fontWeight: '600',
//     color: '#334155',
//     marginBottom: 12,
//   },
//   photoWrapper: {
//     marginBottom: 16,
//     backgroundColor: '#f8fafc',
//     borderRadius: 12,
//     overflow: 'hidden',
//     borderWidth: 1,
//     borderColor: '#e2e8f0',
//   },
//   photo: {
//     width: '100%',
//     height: 200,
//     backgroundColor: '#f1f5f9',
//   },
//   photoUrl: {
//     fontSize: 10,
//     color: '#64748b',
//     padding: 8,
//     textAlign: 'center',
//   },
//   noPhotos: {
//     alignItems: 'center',
//     justifyContent: 'center',
//     padding: 40,
//     backgroundColor: '#f8fafc',
//     borderRadius: 12,
//     borderWidth: 1,
//     borderColor: '#e2e8f0',
//   },
//   noPhotosText: {
//     marginTop: 8,
//     fontSize: 14,
//     color: '#94a3b8',
//   },
//   navigateBtn: {
//     flexDirection: 'row',
//     alignItems: 'center',
//     justifyContent: 'center',
//     backgroundColor: '#10b981',
//     padding: 14,
//     borderRadius: 12,
//     gap: 8,
//     marginTop: 8,
//   },
//   navigateBtnText: {
//     color: '#fff',
//     fontSize: 16,
//     fontWeight: '600',
//   },
// });