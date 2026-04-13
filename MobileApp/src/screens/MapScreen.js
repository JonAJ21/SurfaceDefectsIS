import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { View, StyleSheet, Alert, Platform, TouchableOpacity, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { WebView } from 'react-native-webview';
import { getNearbyDefects, DEFECT_TYPE_LABELS } from '../services/defectsService';
import { WebViewMessageTypes, ReactToWebViewTypes } from '../assets/map/map-bridge';
import * as Location from 'expo-location';
import { useAuth } from '../context/AuthContext';

// 🔹 ЕДИНЫЙ HTML ДЛЯ WEB И ANDROID (принимает initialCenter)
const getMapHTML = (baseUrl, initialCenter = [37.6, 55.6]) => {
  return `
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>RoadDefects Map</title>
      <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" />
      <script src="https://unpkg.com/@turf/turf@6/turf.min.js"><\/script>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body, #map { width: 100%; height: 100%; background: #f1f5f9; }
      </style>
    </head>
    <body>
      <div id="map"></div>
      <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"><\/script>
      <script src="https://unpkg.com/pmtiles@2.11.0/dist/index.js"><\/script>
      <script>
        var protocol = new pmtiles.Protocol({ cacheSize: 1024 });
        maplibregl.addProtocol("pmtiles", protocol.tile);
        
        var map = new maplibregl.Map({
          container: 'map',
          style: {
            version: 8,
            glyphs: '${baseUrl}/fonts/{fontstack}/{range}.pbf',
            sources: { 'pmtiles': { type: 'vector', url: 'pmtiles://${baseUrl}/pmtiles/moscow_oblast.pmtiles' } },
            layers: [
              { id: 'water', type: 'fill', source: 'pmtiles', 'source-layer': 'water', paint: { 'fill-color': '#dbeafe' } },
              { id: 'waterway', type: 'line', source: 'pmtiles', 'source-layer': 'waterway', paint: { 'line-color': '#93c5fd', 'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.5, 14, 2] } },
              { id: 'water_name', type: 'symbol', source: 'pmtiles', 'source-layer': 'water_name', minzoom: 14, layout: { 'text-field': ['get', 'name'], 'text-font': ['Noto Sans Italic'], 'text-size': 12 }, paint: { 'text-color': '#1e40af', 'text-halo-color': '#fff', 'text-halo-width': 1 } },
              { id: 'landcover', type: 'fill', source: 'pmtiles', 'source-layer': 'landcover', paint: { 'fill-color': '#dcfce7', 'fill-opacity': 0.5 } },
              { id: 'landuse', type: 'fill', source: 'pmtiles', 'source-layer': 'landuse', paint: { 'fill-color': '#f1f5f9', 'fill-opacity': 0.5 } },
              { id: 'park', type: 'fill', source: 'pmtiles', 'source-layer': 'park', paint: { 'fill-color': '#86efac', 'fill-opacity': 0.6 } },
              { id: 'building', type: 'fill', source: 'pmtiles', 'source-layer': 'building', paint: { 'fill-color': '#e2e8f0', 'fill-outline-color': '#cbd5e1' } },
              { id: 'aeroway', type: 'fill', source: 'pmtiles', 'source-layer': 'aeroway', paint: { 'fill-color': '#fbbf24', 'fill-opacity': 0.5 } },
              { id: 'aerodrome_label', type: 'symbol', source: 'pmtiles', 'source-layer': 'aerodrome_label', minzoom: 10, layout: { 'text-field': ['get', 'name'], 'text-font': ['Noto Sans Regular'], 'text-size': 11 }, paint: { 'text-color': '#92400e', 'text-halo-color': '#fff', 'text-halo-width': 1.5 } },
              { id: 'road_motorway', type: 'line', source: 'pmtiles', 'source-layer': 'transportation', filter: ['==', 'class', 'motorway'], paint: { 'line-color': '#fca5a5', 'line-width': ['interpolate', ['linear'], ['zoom'], 6, 1, 10, 4, 16, 14] } },
              { id: 'road_trunk', type: 'line', source: 'pmtiles', 'source-layer': 'transportation', filter: ['==', 'class', 'trunk'], paint: { 'line-color': '#fdba74', 'line-width': ['interpolate', ['linear'], ['zoom'], 6, 0.5, 10, 3, 16, 12] } },
              { id: 'road_primary', type: 'line', source: 'pmtiles', 'source-layer': 'transportation', filter: ['==', 'class', 'primary'], paint: { 'line-color': '#fef3c7', 'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.5, 12, 2, 16, 10] } },
              { id: 'road_secondary', type: 'line', source: 'pmtiles', 'source-layer': 'transportation', filter: ['==', 'class', 'secondary'], paint: { 'line-color': '#fef3c7', 'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.5, 12, 2, 16, 8] } },
              { id: 'road_tertiary', type: 'line', source: 'pmtiles', 'source-layer': 'transportation', filter: ['==', 'class', 'tertiary'], paint: { 'line-color': '#fff', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 14, 2, 18, 6] } },
              { id: 'road_minor', type: 'line', source: 'pmtiles', 'source-layer': 'transportation', filter: ['in', 'class', 'minor', 'service', 'track'], paint: { 'line-color': '#fff', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 14, 2, 18, 6] } },
              { id: 'road_path', type: 'line', source: 'pmtiles', 'source-layer': 'transportation', filter: ['in', 'class', 'path', 'footway', 'cycleway'], paint: { 'line-color': '#cbd5e1', 'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.5, 16, 2], 'line-dasharray': [2, 2] } },
              { id: 'road_rail', type: 'line', source: 'pmtiles', 'source-layer': 'transportation', filter: ['==', 'class', 'rail'], paint: { 'line-color': '#cbd5e1', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 14, 1.5], 'line-dasharray': [2, 2] } },
              { id: 'road_name_motorway', type: 'symbol', source: 'pmtiles', 'source-layer': 'transportation_name', filter: ['==', 'class', 'motorway'], minzoom: 13, layout: { 'text-field': ['get', 'name'], 'text-font': ['Noto Sans Bold'], 'text-size': 12, 'symbol-placement': 'line', 'text-rotation-alignment': 'map' }, paint: { 'text-color': '#7f1d1d', 'text-halo-color': '#fff', 'text-halo-width': 1.5 } },
              { id: 'road_name_major', type: 'symbol', source: 'pmtiles', 'source-layer': 'transportation_name', filter: ['in', 'class', 'primary', 'secondary', 'tertiary'], minzoom: 14, layout: { 'text-field': ['get', 'name'], 'text-font': ['Noto Sans Regular'], 'text-size': 11, 'symbol-placement': 'line', 'text-rotation-alignment': 'map' }, paint: { 'text-color': '#334155', 'text-halo-color': '#fff', 'text-halo-width': 1.5 } },
              { id: 'road_name_minor', type: 'symbol', source: 'pmtiles', 'source-layer': 'transportation_name', filter: ['in', 'class', 'minor', 'service'], minzoom: 15, layout: { 'text-field': ['get', 'name'], 'text-font': ['Noto Sans Regular'], 'text-size': 10, 'symbol-placement': 'line', 'text-rotation-alignment': 'map' }, paint: { 'text-color': '#64748b', 'text-halo-color': '#fff', 'text-halo-width': 1 } },
              { id: 'boundary', type: 'line', source: 'pmtiles', 'source-layer': 'boundary', paint: { 'line-color': '#64748b', 'line-width': ['interpolate', ['linear'], ['zoom'], 4, 1, 8, 2], 'line-dasharray': [3, 2] } },
              { id: 'place_city', type: 'symbol', source: 'pmtiles', 'source-layer': 'place', filter: ['==', 'class', 'city'], minzoom: 6, layout: { 'text-field': ['get', 'name'], 'text-font': ['Noto Sans Bold'], 'text-size': ['interpolate', ['linear'], ['zoom'], 6, 14, 12, 22], 'text-anchor': 'center' }, paint: { 'text-color': '#0f172a', 'text-halo-color': '#fff', 'text-halo-width': 2 } },
              { id: 'place_town', type: 'symbol', source: 'pmtiles', 'source-layer': 'place', filter: ['==', 'class', 'town'], minzoom: 8, layout: { 'text-field': ['get', 'name'], 'text-font': ['Noto Sans Regular'], 'text-size': ['interpolate', ['linear'], ['zoom'], 8, 12, 12, 16], 'text-anchor': 'center' }, paint: { 'text-color': '#334155', 'text-halo-color': '#fff', 'text-halo-width': 1.5 } },
              { id: 'place_village', type: 'symbol', source: 'pmtiles', 'source-layer': 'place', filter: ['in', 'class', 'village', 'hamlet', 'suburb'], minzoom: 10, layout: { 'text-field': ['get', 'name'], 'text-font': ['Noto Sans Regular'], 'text-size': ['interpolate', ['linear'], ['zoom'], 10, 10, 14, 14], 'text-anchor': 'center' }, paint: { 'text-color': '#64748b', 'text-halo-color': '#fff', 'text-halo-width': 1 } }
            ]
          },
          center: [${initialCenter[0]}, ${initialCenter[1]}],
          zoom: 16,
          minZoom: 8,
          maxZoom: 19
        });

        var locationMode = 0;
        var currentSpeed = 0;
        window.prevCoords = null;
        var isFirstFix = true;

        var handleMessage = function(e) {
          try {
            var rawData = e && e.data ? e.data : null;
            if (!rawData) return;
            var data = typeof rawData === 'string' ? JSON.parse(rawData) : rawData;
            if (!data || !data.type) return;

            if (data.type === 'ZOOM_IN') { map.zoomIn(); return; }
            if (data.type === 'ZOOM_OUT') { map.zoomOut(); return; }
            
            if (data.type === 'TOGGLE_LOCATION_MODE') {
              locationMode = (locationMode + 1) % 3;
              sendToReact('LOCATION_MODE_CHANGED', locationMode);
              if (window.prevCoords) updateLocation(window.prevCoords[0], window.prevCoords[1], currentSpeed);
              return;
            }
            
            if (data.type === 'SET_USER_LOCATION' && data.payload) {
              updateLocation(data.payload.lng, data.payload.lat, data.payload.speed ?? currentSpeed);
              return;
            }
            
            if (data.type === 'SET_DEFECTS' && Array.isArray(data.payload)) {
              var features = data.payload.filter(d => d.lat && d.lon).map(d => ({
                type: 'Feature', geometry: { type: 'Point', coordinates: [parseFloat(d.lon), parseFloat(d.lat)] }, properties: d
              }));
              var source = map.getSource('defects');
              if (source) source.setData({ type: 'FeatureCollection', features: features });
              return;
            }
          } catch(err) { console.error('Map msg error:', err); }
        };

        if (document.addEventListener) document.addEventListener('message', handleMessage, false);
        if (window.addEventListener) window.addEventListener('message', handleMessage, false);

        function updateLocation(lng, lat, speed) {
          currentSpeed = speed;
          
          if (map.getLayer('user-marker-circle')) map.removeLayer('user-marker-circle');
          if (map.getLayer('user-marker-accuracy')) map.removeLayer('user-marker-accuracy');
          if (map.getSource('user-location')) map.removeSource('user-location');
          
          map.addSource('user-location', { type: 'geojson', data: { type: 'Feature', geometry: { type: 'Point', coordinates: [lng, lat] } } });
          map.addLayer({ id: 'user-marker-circle', type: 'circle', source: 'user-location', paint: { 'circle-radius': 8, 'circle-color': '#4c8bf5', 'circle-stroke-width': 3, 'circle-stroke-color': '#ffffff' } });
          map.addLayer({ id: 'user-marker-accuracy', type: 'circle', source: 'user-location', paint: { 'circle-radius': 25, 'circle-color': '#4c8bf5', 'circle-opacity': 0.15 } }, 'user-marker-circle');

          if (!window.prevCoords) window.prevCoords = [lng, lat];
          
          if (isFirstFix) {
            map.jumpTo({ center: [lng, lat], zoom: 16 });
            isFirstFix = false;
          } else if (locationMode === 1) {
            map.easeTo({ center: [lng, lat], bearing: 0, pitch: 0, zoom: Math.max(map.getZoom(), 16), duration: 400 });
          } 
          else if (locationMode === 2) {
            var dist = turf.distance(turf.point(window.prevCoords), turf.point([lng, lat]), { units: 'meters' });
            var targetBearing = map.getBearing();
            if (dist > 2 && speed > 1.5) {
              targetBearing = turf.bearing(turf.point(window.prevCoords), turf.point([lng, lat]));
            }
            map.easeTo({ center: [lng, lat], bearing: targetBearing, pitch: 0, zoom: Math.max(map.getZoom(), 17), duration: 400 });
          }
          
          window.prevCoords = [lng, lat];
        }

        function sendToReact(type, payload) {
          var msg = JSON.stringify({ type, payload });
          if (window.ReactNativeWebView) window.ReactNativeWebView.postMessage(msg);
          else if (window.parent !== window) window.parent.postMessage(msg, '*');
        }

        map.on('load', function() {
          map.addSource('defects', { type: 'geojson', data: { type: 'FeatureCollection', features: [] }, cluster: true, clusterMaxZoom: 14, clusterRadius: 50 });
          map.addLayer({ id: 'defects-clusters', type: 'circle', source: 'defects', filter: ['has', 'point_count'], paint: { 'circle-color': ['step', ['get', 'point_count'], '#3b82f6', 10, '#f59e0b', 100, '#ef4444'], 'circle-radius': ['step', ['get', 'point_count'], 12, 10, 16, 100, 22] } });
          map.addLayer({ id: 'defects-count', type: 'symbol', source: 'defects', filter: ['has', 'point_count'], layout: { 'text-field': '{point_count_abbreviated}', 'text-font': ['Noto Sans Bold'], 'text-size': 12 }, paint: { 'text-color': '#fff' } });
          map.addLayer({ id: 'defects-points', type: 'circle', source: 'defects', filter: ['!', ['has', 'point_count']], paint: { 'circle-radius': 9, 'circle-color': '#ef4444', 'circle-stroke-width': 2, 'circle-stroke-color': '#fff' } });
          sendToReact('MAP_READY', null);
        });
        
        map.on('click', 'defects-points', function(e) {
          var props = e.features[0].properties;
          sendToReact('DEFECT_CLICK', { id: props.id, lat: e.lngLat.lat, lng: e.lngLat.lng, type: props.type, description: props.description, road_name: props.road_name });
        });
      <\/script>
    </body>
    </html>
  `;
};

export default function MapScreen({ navigation }) {
  const webViewRef = useRef(null);
  const [mapReady, setMapReady] = useState(false);
  const [defects, setDefects] = useState([]);
  const [userLocation, setUserLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [locationMode, setLocationMode] = useState(0);
  const [currentSpeed, setCurrentSpeed] = useState(0);
  const { user } = useAuth();

  const locationSubscription = useRef(null);
  const lastPosRef = useRef(null);

  const baseUrl = useMemo(() => {
    return Platform.OS === 'web' ? 'http://localhost:9000' : 'http://10.0.2.2:9000';
  }, []);

  // 🔹 Получаем последнюю известную позицию для начального центра
  const initialCenter = useMemo(() => {
    if (lastPosRef.current) {
      return [lastPosRef.current.lon, lastPosRef.current.lat];
    }
    return [37.6, 55.6]; // Дефолт (Москва), если координат ещё нет
  }, []);

  const mapHtml = useMemo(() => getMapHTML(baseUrl, initialCenter), [baseUrl, initialCenter]);

  const fetchNearbyDefects = useCallback(async (lat, lng, radius = 500) => {
    try {
      const data = await getNearbyDefects({ latitude: lat, longitude: lng, radius_meters: radius });
      setDefects(data.map(d => ({
        id: d.id, lat: d.snapped_coordinates?.[1] || d.original_coordinates?.[1], lon: d.snapped_coordinates?.[0] || d.original_coordinates?.[0],
        type: DEFECT_TYPE_LABELS[d.defect_type] || d.defect_type, severity: d.severity, description: d.description, status: d.status,
        road_name: d.road_name, distance_meters: d.distance_meters, photos: d.photos || [], created_at: d.created_at
      })));
    } catch (e) { console.error('Fetch nearby defects error:', e); }
  }, []);

  const startLocationTracking = useCallback(async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') { fetchNearbyDefects(55.6, 37.6); setLoading(false); return; }

      locationSubscription.current = await Location.watchPositionAsync(
        { accuracy: Location.Accuracy.High, timeInterval: 1500, distanceInterval: 2 },
        (loc) => {
          const { latitude, longitude, speed, timestamp } = loc.coords;
          let calcSpeed = speed != null ? speed * 3.6 : 0;
          
          if (lastPosRef.current) {
            const R = 6371000;
            const dLat = (latitude - lastPosRef.current.lat) * (Math.PI / 180);
            const dLon = (longitude - lastPosRef.current.lon) * (Math.PI / 180);
            const a = Math.sin(dLat / 2) ** 2 + Math.cos(lastPosRef.current.lat * (Math.PI / 180)) * Math.cos(latitude * (Math.PI / 180)) * Math.sin(dLon / 2) ** 2;
            const dist = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            const timeDiff = (timestamp - lastPosRef.current.timestamp) / 1000;
            if (timeDiff > 0) calcSpeed = (dist / timeDiff) * 3.6;
          }

          if (calcSpeed < 1) calcSpeed = 0;
          lastPosRef.current = { lat: latitude, lon: longitude, timestamp };
          setCurrentSpeed(Math.round(calcSpeed));
          
          sendToMap(ReactToWebViewTypes.SET_USER_LOCATION, { lat: latitude, lng: longitude, speed: Math.round(calcSpeed) });
          setUserLocation({ lat: latitude, lng: longitude, speed: Math.round(calcSpeed) });
        }
      );
    } catch (e) {
      console.error('Location tracking error:', e);
      fetchNearbyDefects(55.6, 37.6);
    } finally { setLoading(false); }
  }, [fetchNearbyDefects]);

  const sendToMap = useCallback((type, payload) => {
    const msg = JSON.stringify({ type, payload });
    if (Platform.OS === 'web') {
      const iframe = document.querySelector('iframe#map-iframe');
      if (iframe?.contentWindow) iframe.contentWindow.postMessage(msg, '*');
    } else {
      if (webViewRef.current) webViewRef.current.postMessage(msg);
    }
  }, []);

  const handleMapMessage = useCallback((data) => {
    try {
      if (typeof data !== 'string') return;
      const msg = JSON.parse(data);
      if (!msg || !msg.type) return;
      if (msg.type === WebViewMessageTypes.MAP_READY) { setMapReady(true); startLocationTracking(); }
      if (msg.type === WebViewMessageTypes.DEFECT_CLICK) {
        Alert.alert(msg.payload.type || 'Дефект', `${msg.payload.description || ''}\n📍 ${msg.payload.road_name || ''}`, [{ text: 'Закрыть', style: 'cancel' }]);
      }
      if (msg.type === 'LOCATION_MODE_CHANGED') setLocationMode(msg.payload);
    } catch (e) {}
  }, [startLocationTracking]);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    const listener = (e) => handleMapMessage(e.data);
    window.addEventListener('message', listener);
    return () => window.removeEventListener('message', listener);
  }, [handleMapMessage]);

  useEffect(() => { if (mapReady && defects.length > 0) sendToMap(ReactToWebViewTypes.SET_DEFECTS, defects); }, [defects, mapReady, sendToMap]);
  useEffect(() => { return () => { if (locationSubscription.current) locationSubscription.current.remove(); }; }, []);

  const handleZoomIn = () => sendToMap('ZOOM_IN', null);
  const handleZoomOut = () => sendToMap('ZOOM_OUT', null);
  const handleLocationToggle = () => sendToMap('TOGGLE_LOCATION_MODE', null);

  const getLocationIcon = () => locationMode === 0 ? 'location-outline' : locationMode === 1 ? 'compass-outline' : 'navigate';
  const getLocationBg = () => locationMode === 0 ? '#fff' : '#eff6ff';

  return (
    <View style={styles.container}>
      {Platform.OS === 'web' ? (
        <iframe id="map-iframe" srcDoc={mapHtml} style={styles.iframe} title="Map" onLoad={() => console.log('🗺️ Iframe loaded')} sandbox="allow-scripts allow-same-origin allow-popups" />
      ) : (
        <WebView ref={webViewRef} originWhitelist={['*', 'http://*', 'https://*', 'pmtiles://*']} source={{ html: mapHtml }} style={styles.webview} onMessage={(e) => handleMapMessage(e.nativeEvent.data)} javaScriptEnabled={true} domStorageEnabled={true} allowsFullscreenVideo={true} bounces={false} scrollEnabled={false} mixedContentMode="compatibility" allowsInlineMediaPlayback={true} mediaPlaybackRequiresUserAction={false} androidLayerType="hardware" onLoadEnd={() => setMapReady(true)} />
      )}

      <TouchableOpacity style={styles.profileButton} onPress={() => user ? navigation.navigate('Profile') : navigation.navigate('Login')} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
        {user ? <View style={styles.avatarContainer}><Text style={styles.avatarText}>{(user.full_name || user.email || 'U').charAt(0).toUpperCase()}</Text></View> : <Ionicons name="person-outline" size={24} color="#0f172a" />}
      </TouchableOpacity>

      <View style={styles.zoomContainer}>
        <TouchableOpacity style={styles.zoomBtn} onPress={handleZoomIn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}><Ionicons name="add" size={24} color="#0f172a" /></TouchableOpacity>
        <View style={styles.zoomDivider} />
        <TouchableOpacity style={styles.zoomBtn} onPress={handleZoomOut} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}><Ionicons name="remove" size={24} color="#0f172a" /></TouchableOpacity>
      </View>

      <TouchableOpacity style={[styles.locationButton, { backgroundColor: getLocationBg() }]} onPress={handleLocationToggle} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
        <Ionicons name={getLocationIcon()} size={24} color={locationMode === 0 ? '#0f172a' : '#2563eb'} />
      </TouchableOpacity>

      <TouchableOpacity style={styles.fab} onPress={() => user ? navigation.navigate('CreateDefect', { initialCoords: userLocation || { lat: 55.6, lng: 37.6 } }) : Alert.alert('Авторизация', 'Войдите, чтобы добавить дефект', [{ text: 'Войти', onPress: () => navigation.navigate('Login') }])} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
        <Ionicons name="add" size={28} color="#fff" />
      </TouchableOpacity>

      {locationMode === 2 && currentSpeed > 1.5 && <View style={styles.speedBadge}><Text style={styles.speedText}>{currentSpeed} км/ч</Text></View>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  webview: { flex: 1 }, iframe: { flex: 1, borderWidth: 0, width: '100%', height: '100%' },
  profileButton: { position: 'absolute', top: 16, right: 16, width: 48, height: 48, borderRadius: 24, backgroundColor: '#fff', justifyContent: 'center', alignItems: 'center', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, zIndex: 60, borderWidth: 1, borderColor: '#e2e8f0' },
  avatarContainer: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#2563eb', justifyContent: 'center', alignItems: 'center' }, avatarText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  zoomContainer: { position: 'absolute', right: 16, top: '40%', backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: '#e2e8f0', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, zIndex: 60, overflow: 'hidden' },
  zoomBtn: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center' }, zoomDivider: { height: 1, backgroundColor: '#e2e8f0' },
  locationButton: { position: 'absolute', bottom: 96, right: 16, width: 48, height: 48, borderRadius: 24, justifyContent: 'center', alignItems: 'center', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, zIndex: 60, borderWidth: 1, borderColor: '#e2e8f0' },
  fab: { position: 'absolute', bottom: 24, left: 24, width: 56, height: 56, borderRadius: 28, backgroundColor: '#2563eb', justifyContent: 'center', alignItems: 'center', elevation: 6, shadowColor: '#000', shadowOffset: { width: 0, height: 3 }, shadowOpacity: 0.25, shadowRadius: 4, zIndex: 50 },
  speedBadge: { position: 'absolute', bottom: 150, right: 16, backgroundColor: 'rgba(0,0,0,0.7)', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, zIndex: 60 }, speedText: { color: '#fff', fontSize: 12, fontWeight: '700' }
});