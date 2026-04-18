// MobileApp/src/screens/MapScreen.js
import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { View, StyleSheet, Alert, Platform, TouchableOpacity, Text, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { WebView } from 'react-native-webview';
import { getNearbyDefects, DEFECT_TYPE_LABELS, snapPoint } from '../services/defectsService';
import { WebViewMessageTypes, ReactToWebViewTypes } from '../assets/map/map-bridge';
import * as Location from 'expo-location';
import { useAuth } from '../context/AuthContext';

// Компонент Toast уведомлений
const Toast = ({ visible, message, type, onHide }) => {
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 1,
          duration: 300,
          useNativeDriver: Platform.OS !== 'web',
        }),
        Animated.delay(3000),
        Animated.timing(opacity, {
          toValue: 0,
          duration: 300,
          useNativeDriver: Platform.OS !== 'web',
        }),
      ]).start(() => onHide());
    }
  }, [visible, opacity, onHide]);

  if (!visible) return null;

  const backgroundColor = type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6';
  const icon = type === 'success' ? 'checkmark-circle' : type === 'error' ? 'alert-circle' : 'information-circle';

  return (
    <Animated.View style={[styles.toast, { backgroundColor, opacity }]}>
      <Ionicons name={icon} size={20} color="#fff" />
      <Text style={styles.toastText}>{message}</Text>
    </Animated.View>
  );
};

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
        .draw-instructions {
          position: absolute;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0,0,0,0.8);
          color: white;
          padding: 8px 16px;
          border-radius: 20px;
          font-size: 12px;
          pointer-events: none;
          z-index: 100;
          font-family: sans-serif;
        }
        .snap-indicator {
          position: absolute;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0,0,0,0.7);
          color: #10b981;
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 11px;
          pointer-events: none;
          z-index: 100;
          font-family: sans-serif;
          display: none;
        }
        .snap-error {
          background: rgba(239,68,68,0.9);
          color: white;
        }
      </style>
    </head>
    <body>
      <div id="map"></div>
      <div id="draw-instructions" class="draw-instructions" style="display: none;"></div>
      <div id="snap-indicator" class="snap-indicator"></div>
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

        var drawMode = false;
        var drawPoints = [];
        var drawLayerId = 'draw-layer';
        var drawLineLayerId = 'draw-line-layer';
        
        var locationMode = 0;
        var currentSpeed = 0;
        window.prevCoords = null;
        var isFirstFix = true;

        function showSnapIndicator(message, isError = false) {
          var el = document.getElementById('snap-indicator');
          if (el) {
            el.textContent = message;
            if (isError) {
              el.classList.add('snap-error');
            } else {
              el.classList.remove('snap-error');
            }
            el.style.display = 'block';
            setTimeout(() => {
              el.style.display = 'none';
            }, 2000);
          }
        }

        function updateDrawInstructions() {
          var el = document.getElementById('draw-instructions');
          if (!el) return;
          if (drawMode) {
            var pointCount = drawPoints.length;
            if (pointCount === 0) {
              el.textContent = '🔴 Кликайте на карте, чтобы отметить точки дефекта. Нажмите "Готово" когда закончите';
            } else if (pointCount === 1) {
              el.textContent = '📍 Отмечена 1 точка. Продолжайте или нажмите "Готово" для точечного дефекта';
            } else {
              el.textContent = '📏 Отмечено ' + pointCount + ' точек. Нажмите "Готово" для линейного дефекта';
            }
            el.style.display = 'block';
          } else {
            el.style.display = 'none';
          }
        }

        function clearDraw() {
          drawPoints = [];
          if (map.getSource('draw-source')) {
            if (map.getLayer(drawLayerId)) map.removeLayer(drawLayerId);
            if (map.getLayer(drawLineLayerId)) map.removeLayer(drawLineLayerId);
            map.removeSource('draw-source');
          }
          updateDrawInstructions();
        }

        function updateDrawVisualization() {
          if (!map.getSource('draw-source')) {
            map.addSource('draw-source', {
              type: 'geojson',
              data: { type: 'FeatureCollection', features: [] }
            });
          }
          
          var features = [];
          
          if (drawPoints.length > 0) {
            if (drawPoints.length >= 2) {
              features.push({
                type: 'Feature',
                geometry: { type: 'LineString', coordinates: drawPoints },
                properties: { type: 'draw-line' }
              });
            }
            
            drawPoints.forEach((point, idx) => {
              features.push({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: point },
                properties: { type: 'draw-point', index: idx }
              });
            });
          }
          
          map.getSource('draw-source').setData({
            type: 'FeatureCollection',
            features: features
          });
          
          if (!map.getLayer(drawLayerId)) {
            map.addLayer({
              id: drawLayerId,
              type: 'circle',
              source: 'draw-source',
              filter: ['==', ['get', 'type'], 'draw-point'],
              paint: {
                'circle-radius': 10,
                'circle-color': '#f59e0b',
                'circle-stroke-width': 2,
                'circle-stroke-color': '#fff'
              }
            });
          }
          
          if (drawPoints.length >= 2 && !map.getLayer(drawLineLayerId)) {
            map.addLayer({
              id: drawLineLayerId,
              type: 'line',
              source: 'draw-source',
              filter: ['==', ['get', 'type'], 'draw-line'],
              paint: {
                'line-color': '#f59e0b',
                'line-width': 4,
                'line-dasharray': [2, 2]
              }
            });
          } else if (drawPoints.length < 2 && map.getLayer(drawLineLayerId)) {
            map.removeLayer(drawLineLayerId);
          }
        }

        async function handleMapClick(e) {
          if (!drawMode) return;
          
          var coords = [e.lngLat.lng, e.lngLat.lat];
          
          var snapResult = await performSnap(coords[0], coords[1]);
          
          if (snapResult && snapResult.success === true && snapResult.snapped_longitude && snapResult.snapped_latitude) {
            var finalCoords = [snapResult.snapped_longitude, snapResult.snapped_latitude];
            if (snapResult.road_info && snapResult.road_info.road_name) {
              showSnapIndicator('📍 Привязано к дороге: ' + snapResult.road_info.road_name, false);
            } else {
              showSnapIndicator('📍 Точка привязана к дороге', false);
            }
            
            drawPoints.push(finalCoords);
            updateDrawVisualization();
            updateDrawInstructions();
            
            if (window.sendToReact) {
              window.sendToReact('DRAW_POINT_ADDED', { 
                coordinates: finalCoords, 
                original: coords,
                snapped: snapResult,
                pointCount: drawPoints.length 
              });
            }
          } else {
            var errorMsg = (snapResult && snapResult.message) ? snapResult.message : 'Не удалось привязать точку к дороге';
            showSnapIndicator('⚠️ ' + errorMsg, true);
            
            if (window.sendToReact) {
              window.sendToReact('DRAW_POINT_FAILED', { 
                coordinates: coords,
                error: errorMsg
              });
            }
          }
        }

        async function performSnap(lng, lat) {
          return new Promise((resolve) => {
            if (window.sendToReact) {
              window.sendToReact('SNAP_POINT', { longitude: lng, latitude: lat });
              window.snapCallback = resolve;
            } else {
              resolve(null);
            }
          });
        }

        function completeDraw() {
          if (!drawMode) return;
          
          if (drawPoints.length === 0) {
            if (window.sendToReact) {
              window.sendToReact('DRAW_INCOMPLETE', { message: 'Добавьте хотя бы одну точку' });
            }
            return;
          }
          
          var geometryType = drawPoints.length === 1 ? 'point' : 'linestring';
          
          if (window.sendToReact) {
            window.sendToReact('DRAW_COMPLETE', { 
              type: geometryType, 
              coordinates: drawPoints 
            });
          }
        }

        function sendToReact(type, payload) {
          var msg = JSON.stringify({ type, payload });
          if (window.ReactNativeWebView) window.ReactNativeWebView.postMessage(msg);
          else if (window.parent !== window) window.parent.postMessage(msg, '*');
        }
        
        window.sendToReact = sendToReact;

        var handleMessage = function(e) {
          try {
            var rawData = e && e.data ? e.data : null;
            if (!rawData) return;
            var data = typeof rawData === 'string' ? JSON.parse(rawData) : rawData;
            if (!data || !data.type) return;

            if (data.type === 'ZOOM_IN') { map.zoomIn(); return; }
            if (data.type === 'ZOOM_OUT') { map.zoomOut(); return; }
            
            if (data.type === 'CENTER_MAP') {
              map.flyTo({
                center: [data.payload.lng, data.payload.lat],
                zoom: data.payload.zoom || 18,
                duration: 1000
              });
              return;
            }
            
            if (data.type === 'TOGGLE_LOCATION_MODE') {
              locationMode = (locationMode + 1) % 3;
              if (window.sendToReact) window.sendToReact('LOCATION_MODE_CHANGED', locationMode);
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
            
            if (data.type === 'SNAP_RESPONSE') {
              if (window.snapCallback) {
                window.snapCallback(data.payload);
                window.snapCallback = null;
              }
              return;
            }
            
            if (data.type === 'ENABLE_DRAW_MODE') {
              drawMode = true;
              clearDraw();
              updateDrawInstructions();
              map.on('click', handleMapClick);
              if (window.sendToReact) window.sendToReact('DRAW_MODE_CHANGED', { enabled: true });
              return;
            }
            
            if (data.type === 'DISABLE_DRAW_MODE') {
              drawMode = false;
              clearDraw();
              map.off('click', handleMapClick);
              if (window.sendToReact) window.sendToReact('DRAW_MODE_CHANGED', { enabled: false });
              return;
            }
            
            if (data.type === 'CLEAR_DRAW') {
              clearDraw();
              return;
            }
            
            if (data.type === 'COMPLETE_DRAW') {
              completeDraw();
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

        map.on('load', function() {
          map.addSource('defects', { type: 'geojson', data: { type: 'FeatureCollection', features: [] }, cluster: true, clusterMaxZoom: 14, clusterRadius: 50 });
          map.addLayer({ id: 'defects-clusters', type: 'circle', source: 'defects', filter: ['has', 'point_count'], paint: { 'circle-color': ['step', ['get', 'point_count'], '#3b82f6', 10, '#f59e0b', 100, '#ef4444'], 'circle-radius': ['step', ['get', 'point_count'], 12, 10, 16, 100, 22] } });
          map.addLayer({ id: 'defects-count', type: 'symbol', source: 'defects', filter: ['has', 'point_count'], layout: { 'text-field': '{point_count_abbreviated}', 'text-font': ['Noto Sans Bold'], 'text-size': 12 }, paint: { 'text-color': '#fff' } });
          map.addLayer({ id: 'defects-points', type: 'circle', source: 'defects', filter: ['!', ['has', 'point_count']], paint: { 'circle-radius': 9, 'circle-color': '#ef4444', 'circle-stroke-width': 2, 'circle-stroke-color': '#fff' } });
          if (window.sendToReact) window.sendToReact('MAP_READY', null);
        });
        
        map.on('click', 'defects-points', function(e) {
          var props = e.features[0].properties;
          if (window.sendToReact) {
            window.sendToReact('DEFECT_CLICK', { id: props.id, lat: e.lngLat.lat, lng: e.lngLat.lng, type: props.type, description: props.description, road_name: props.road_name });
          }
        });
      <\/script>
    </body>
    </html>
  `;
};

export default function MapScreen({ navigation, route }) {
  const webViewRef = useRef(null);
  const [mapReady, setMapReady] = useState(false);
  const [defects, setDefects] = useState([]);
  const [userLocation, setUserLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [locationMode, setLocationMode] = useState(0);
  const [currentSpeed, setCurrentSpeed] = useState(0);
  const [drawMode, setDrawMode] = useState(false);
  const [drawPoints, setDrawPoints] = useState([]);
  const [toast, setToast] = useState({ visible: false, message: '', type: 'info' });
  const [disableTracking, setDisableTracking] = useState(false);
  const { user, isVerified } = useAuth();

  const locationSubscription = useRef(null);
  const lastPosRef = useRef(null);

  const showToast = useCallback((message, type = 'info') => {
    setToast({ visible: true, message, type });
  }, []);

  const baseUrl = useMemo(() => {
    return Platform.OS === 'web' ? 'http://localhost:9000' : 'http://10.0.2.2:9000';
  }, []);

  const initialCenter = useMemo(() => {
    if (lastPosRef.current) {
      return [lastPosRef.current.lon, lastPosRef.current.lat];
    }
    return [37.6, 55.6];
  }, []);

  const mapHtml = useMemo(() => getMapHTML(baseUrl, initialCenter), [baseUrl, initialCenter]);

  // ===== ВСЕ ФУНКЦИИ ОБЪЯВЛЕНЫ ЗДЕСЬ, ПЕРЕД ИХ ИСПОЛЬЗОВАНИЕМ В useEffect =====
  
  const sendToMap = useCallback((type, payload) => {
    const msg = JSON.stringify({ type, payload });
    if (Platform.OS === 'web') {
      const iframe = document.querySelector('iframe#map-iframe');
      if (iframe?.contentWindow) iframe.contentWindow.postMessage(msg, '*');
    } else {
      if (webViewRef.current) webViewRef.current.postMessage(msg);
    }
  }, []);

  const fetchNearbyDefects = useCallback(async (lat, lng, radius = 500) => {
    try {
      const data = await getNearbyDefects({ latitude: lat, longitude: lng, radius_meters: radius });
      setDefects(data.map(d => ({
        id: d.id, 
        lat: d.snapped_coordinates?.[1] || d.original_coordinates?.[1], 
        lon: d.snapped_coordinates?.[0] || d.original_coordinates?.[0],
        type: DEFECT_TYPE_LABELS[d.defect_type] || d.defect_type,
        defect_type: d.defect_type,
        severity: d.severity, 
        description: d.description, 
        status: d.status,
        road_name: d.road_name, 
        distance_meters: d.distance_meters, 
        photos: d.photos || [], 
        created_at: d.created_at
      })));
    } catch (e) { 
      console.error('Fetch nearby defects error:', e);
      showToast('Не удалось загрузить дефекты', 'error');
    }
  }, [showToast]);

  const startLocationTracking = useCallback(async () => {
    // Если отключено слежение - не запускаем
    if (disableTracking) {
      setLoading(false);
      return;
    }
    
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') { 
        showToast('Нет доступа к геолокации', 'error');
        fetchNearbyDefects(55.6, 37.6); 
        setLoading(false); 
        return; 
      }

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
      showToast('Ошибка определения местоположения', 'error');
      fetchNearbyDefects(55.6, 37.6);
    } finally { setLoading(false); }
  }, [fetchNearbyDefects, showToast, sendToMap, disableTracking]);

  const handleSnapPoint = useCallback(async (longitude, latitude) => {
    try {
      const result = await snapPoint({ longitude, latitude, max_distance_meters: 15 });
      
      if (result && result.snapped_longitude && result.snapped_latitude) {
        const distance = result.distance_meters;
        if (distance > 15) {
          showToast(`Точка далеко от дороги (${distance.toFixed(0)} м)`, 'error');
        } else if (result.road_info?.road_name) {
          showToast(`Привязано к дороге: ${result.road_info.road_name}`, 'success');
        } else {
          showToast('Точка привязана к дороге', 'success');
        }
        sendToMap('SNAP_RESPONSE', { success: true, ...result });
        return { success: true, ...result };
      } else {
        let errorMessage = 'Не удалось привязать точку к дороге';
        if (result?.detail) {
          if (typeof result.detail === 'object') {
            errorMessage = result.detail.detail || result.detail.error || errorMessage;
          } else if (typeof result.detail === 'string') {
            errorMessage = result.detail;
          }
        }
        showToast(errorMessage, 'error');
        sendToMap('SNAP_RESPONSE', { success: false, error: true, message: errorMessage });
        return { success: false, error: true, message: errorMessage };
      }
    } catch (error) {
      console.error('Snap error:', error);
      
      let errorMessage = 'Ошибка привязки к дороге';
      
      if (error.response) {
        const status = error.response.status;
        const responseData = error.response.data;
        
        if (status === 404) {
          if (responseData?.detail) {
            const detail = responseData.detail;
            if (typeof detail === 'object' && detail.error === 'Road not found') {
              errorMessage = detail.detail || 'Дорога не найдена. Точка слишком далеко от дорог';
            } else if (typeof detail === 'string') {
              errorMessage = detail;
            } else {
              errorMessage = 'Дорога не найдена. Точка слишком далеко от дорог';
            }
          } else {
            errorMessage = 'Дорога не найдена. Точка слишком далеко от дорог';
          }
        } else if (status === 400) {
          errorMessage = 'Некорректные координаты';
        } else if (status === 401 || status === 403) {
          errorMessage = 'Нет доступа к сервису привязки';
        } else if (status === 500) {
          errorMessage = 'Ошибка сервера. Попробуйте позже';
        } else {
          errorMessage = responseData?.detail || responseData?.message || `Ошибка ${status}`;
          if (typeof errorMessage === 'object') {
            errorMessage = errorMessage.detail || errorMessage.error || 'Неизвестная ошибка';
          }
        }
      } else if (error.request) {
        errorMessage = 'Нет соединения с сервером';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      showToast(errorMessage, 'error');
      sendToMap('SNAP_RESPONSE', { 
        success: false, 
        error: true, 
        message: errorMessage,
        status: error.response?.status
      });
      
      return { success: false, error: true, message: errorMessage };
    }
  }, [sendToMap, showToast]);

  const handleMapMessage = useCallback(async (data) => {
    try {
      if (typeof data !== 'string') return;
      const msg = JSON.parse(data);
      if (!msg || !msg.type) return;
      
      if (msg.type === WebViewMessageTypes.MAP_READY) { 
        setMapReady(true); 
        startLocationTracking(); 
        showToast('Карта загружена', 'success');
      }
      
      if (msg.type === WebViewMessageTypes.DEFECT_CLICK) {
        Alert.alert(
          msg.payload.type || 'Дефект', 
          `${msg.payload.description || ''}\n📍 ${msg.payload.road_name || ''}`,
          [{ text: 'Закрыть', style: 'cancel' }]
        );
      }
      
      if (msg.type === 'LOCATION_MODE_CHANGED') setLocationMode(msg.payload);
      
      if (msg.type === 'SNAP_POINT') {
        await handleSnapPoint(msg.payload.longitude, msg.payload.latitude);
      }
      
      if (msg.type === 'DRAW_POINT_ADDED') {
        setDrawPoints(prev => [...prev, msg.payload.coordinates]);
        const pointCount = drawPoints.length + 1;
        if (pointCount === 1) {
          showToast('Точка добавлена. Продолжайте или нажмите "Готово"', 'success');
        } else {
          showToast(`Добавлена точка ${pointCount}. Будет создан линейный дефект`, 'success');
        }
      }
      
      if (msg.type === 'DRAW_POINT_FAILED') {
        showToast(msg.payload.error || 'Точка не добавлена', 'error');
      }
      
      if (msg.type === 'DRAW_COMPLETE') {
        setDrawMode(false);
        navigation.navigate('CreateDefect', {
          geometryType: msg.payload.type,
          coordinates: msg.payload.coordinates,
          userLocation: userLocation
        });
        sendToMap('DISABLE_DRAW_MODE', null);
      }
      
      if (msg.type === 'DRAW_INCOMPLETE') {
        showToast(msg.payload.message || 'Добавьте хотя бы одну точку', 'error');
      }
      
      if (msg.type === 'DRAW_MODE_CHANGED') {
        if (!msg.payload.enabled) {
          setDrawMode(false);
          setDrawPoints([]);
        }
      }
    } catch (e) {
      console.error('Message handling error:', e);
      showToast('Ошибка обработки данных карты', 'error');
    }
  }, [startLocationTracking, userLocation, navigation, sendToMap, handleSnapPoint, drawPoints.length, showToast]);

  // ===== useEffect ХУКИ - ИСПОЛЬЗУЮТ ФУНКЦИИ, ОБЪЯВЛЕННЫЕ ВЫШЕ =====
  
  // Обработка параметров из навигации
  useEffect(() => {
    if (route.params?.disableLocationTracking) {
      setDisableTracking(true);
      navigation.setParams({ disableLocationTracking: null });
    }
  }, [route.params, navigation]);

  // Обработка центрирования на дефекте из параметров навигации
  useEffect(() => {
    if (route.params?.centerTo && mapReady) {
      const { lat, lng, zoom = 18 } = route.params.centerTo;
      sendToMap('CENTER_MAP', { lat, lng, zoom });
      navigation.setParams({ centerTo: null });
    }
  }, [route.params, mapReady, sendToMap, navigation]);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    const listener = (e) => handleMapMessage(e.data);
    window.addEventListener('message', listener);
    return () => window.removeEventListener('message', listener);
  }, [handleMapMessage]);

  useEffect(() => { 
    if (mapReady && defects.length > 0) sendToMap(ReactToWebViewTypes.SET_DEFECTS, defects); 
  }, [defects, mapReady, sendToMap]);

  useEffect(() => { 
    const subscription = locationSubscription.current;
    return () => { 
      if (subscription) {
        try {
          if (typeof subscription.remove === 'function') {
            subscription.remove();
          }
        } catch (error) {
          console.warn('Error removing location subscription:', error);
        }
      }
    }; 
  }, []);

  // ===== ОСТАЛЬНЫЕ ФУНКЦИИ =====
  
  const startDrawing = () => {
    if (!user || !isVerified) {
      Alert.alert(
        'Требуется верификация',
        'Добавлять дефекты могут только верифицированные пользователи',
        [
          { text: 'Отмена', style: 'cancel' },
          { text: 'Войти', onPress: () => navigation.navigate('Login') }
        ]
      );
      return;
    }
    
    setDrawMode(true);
    setDrawPoints([]);
    sendToMap('ENABLE_DRAW_MODE', null);
    showToast('Режим добавления дефекта. Кликайте на карте', 'info');
  };
  
  const disableDrawMode = () => {
    setDrawMode(false);
    setDrawPoints([]);
    sendToMap('DISABLE_DRAW_MODE', null);
    showToast('Режим добавления дефекта отключён', 'info');
  };
  
  const completeDraw = () => {
    if (drawPoints.length === 0) {
      showToast('Добавьте хотя бы одну точку', 'error');
      return;
    }
    sendToMap('COMPLETE_DRAW', null);
  };
  
  const clearDraw = () => {
    setDrawPoints([]);
    sendToMap('CLEAR_DRAW', null);
    showToast('Все точки удалены', 'info');
  };

  const handleZoomIn = () => sendToMap('ZOOM_IN', null);
  const handleZoomOut = () => sendToMap('ZOOM_OUT', null);
  
  const handleLocationToggle = () => {
    setDisableTracking(false);
    sendToMap('TOGGLE_LOCATION_MODE', null);
  };
  
  const handleMyDefects = () => navigation.navigate('MyDefects');

  const getLocationIcon = () => locationMode === 0 ? 'location-outline' : locationMode === 1 ? 'compass-outline' : 'navigate';
  const getLocationBg = () => locationMode === 0 ? '#fff' : '#eff6ff';

  // ===== РЕНДЕР =====
  return (
    <View style={styles.container}>
      {Platform.OS === 'web' ? (
        <iframe 
          id="map-iframe" 
          srcDoc={mapHtml} 
          style={styles.iframe} 
          title="Map" 
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-modals allow-downloads"
          referrerPolicy="no-referrer"
        />
      ) : (
        <WebView 
          ref={webViewRef} 
          originWhitelist={['*', 'http://*', 'https://*', 'pmtiles://*']} 
          source={{ html: mapHtml }} 
          style={styles.webview} 
          onMessage={(e) => handleMapMessage(e.nativeEvent.data)} 
          javaScriptEnabled={true} 
          domStorageEnabled={true} 
          allowsFullscreenVideo={true} 
          bounces={false} 
          scrollEnabled={false} 
          mixedContentMode="compatibility" 
          allowsInlineMediaPlayback={true} 
          mediaPlaybackRequiresUserAction={false} 
          androidLayerType="hardware" 
          onLoadEnd={() => setMapReady(true)} 
        />
      )}

      <TouchableOpacity style={styles.profileButton} onPress={() => user ? navigation.navigate('Profile') : navigation.navigate('Login')}>
        {user ? <View style={styles.avatarContainer}><Text style={styles.avatarText}>{(user.full_name || user.email || 'U').charAt(0).toUpperCase()}</Text></View> : <Ionicons name="person-outline" size={24} color="#0f172a" />}
      </TouchableOpacity>

      <TouchableOpacity style={styles.myDefectsButton} onPress={handleMyDefects}>
        <Ionicons name="list-outline" size={22} color="#0f172a" />
      </TouchableOpacity>

      <View style={styles.zoomContainer}>
        <TouchableOpacity style={styles.zoomBtn} onPress={handleZoomIn}><Ionicons name="add" size={24} color="#0f172a" /></TouchableOpacity>
        <View style={styles.zoomDivider} />
        <TouchableOpacity style={styles.zoomBtn} onPress={handleZoomOut}><Ionicons name="remove" size={24} color="#0f172a" /></TouchableOpacity>
      </View>

      <TouchableOpacity style={[styles.locationButton, { backgroundColor: getLocationBg() }]} onPress={handleLocationToggle}>
        <Ionicons name={getLocationIcon()} size={24} color={locationMode === 0 ? '#0f172a' : '#2563eb'} />
      </TouchableOpacity>

      <TouchableOpacity 
        style={[styles.fab, drawMode && styles.fabActive]} 
        onPress={drawMode ? disableDrawMode : startDrawing}
      >
        <Ionicons name={drawMode ? "close" : "add"} size={28} color="#fff" />
      </TouchableOpacity>

      {drawMode && (
        <View style={styles.drawPanel}>
          <View style={styles.drawPanelHeader}>
            <Text style={styles.drawPanelTitle}>
              {drawPoints.length === 0 && '🔴 Добавление дефекта'}
              {drawPoints.length === 1 && '📍 Точечный дефект (1 точка)'}
              {drawPoints.length >= 2 && `📏 Линейный дефект (${drawPoints.length} точек)`}
            </Text>
            <TouchableOpacity onPress={disableDrawMode}>
              <Ionicons name="close" size={24} color="#64748b" />
            </TouchableOpacity>
          </View>
          <Text style={styles.drawPanelInfo}>
            {drawPoints.length === 0 && 'Кликните на карте, чтобы отметить точки дефекта'}
            {drawPoints.length === 1 && 'Добавьте ещё точки для линейного дефекта или нажмите "Готово"'}
            {drawPoints.length >= 2 && 'Нажмите "Готово", чтобы завершить создание дефекта'}
          </Text>
          <View style={styles.drawPanelActions}>
            <TouchableOpacity style={styles.drawPanelClear} onPress={clearDraw}>
              <Ionicons name="trash-outline" size={18} color="#ef4444" />
              <Text style={styles.drawPanelClearText}>Очистить</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.drawPanelComplete, drawPoints.length === 0 && styles.drawPanelCompleteDisabled]} 
              onPress={completeDraw}
              disabled={drawPoints.length === 0}
            >
              <Ionicons name="checkmark" size={18} color="#fff" />
              <Text style={styles.drawPanelCompleteText}>Готово</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {locationMode === 2 && currentSpeed > 1.5 && (
        <View style={styles.speedBadge}>
          <Text style={styles.speedText}>{currentSpeed} км/ч</Text>
        </View>
      )}

      <Toast 
        visible={toast.visible} 
        message={toast.message} 
        type={toast.type} 
        onHide={() => setToast(prev => ({ ...prev, visible: false }))} 
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  webview: { flex: 1 }, 
  iframe: { flex: 1, borderWidth: 0, width: '100%', height: '100%' },
  
  profileButton: { position: 'absolute', top: 16, right: 16, width: 48, height: 48, borderRadius: 24, backgroundColor: '#fff', justifyContent: 'center', alignItems: 'center', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, zIndex: 60, borderWidth: 1, borderColor: '#e2e8f0' },
  myDefectsButton: { position: 'absolute', top: 16, left: 16, width: 48, height: 48, borderRadius: 24, backgroundColor: '#fff', justifyContent: 'center', alignItems: 'center', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, zIndex: 60, borderWidth: 1, borderColor: '#e2e8f0' },
  avatarContainer: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#2563eb', justifyContent: 'center', alignItems: 'center' }, 
  avatarText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  
  zoomContainer: { position: 'absolute', right: 16, top: '40%', backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: '#e2e8f0', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, zIndex: 60, overflow: 'hidden' },
  zoomBtn: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center' }, 
  zoomDivider: { height: 1, backgroundColor: '#e2e8f0' },
  
  locationButton: { position: 'absolute', bottom: 96, right: 16, width: 48, height: 48, borderRadius: 24, justifyContent: 'center', alignItems: 'center', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, zIndex: 60, borderWidth: 1, borderColor: '#e2e8f0' },
  
  fab: { position: 'absolute', bottom: 24, right: 24, width: 56, height: 56, borderRadius: 28, backgroundColor: '#2563eb', justifyContent: 'center', alignItems: 'center', elevation: 6, shadowColor: '#000', shadowOffset: { width: 0, height: 3 }, shadowOpacity: 0.25, shadowRadius: 4, zIndex: 50 },
  fabActive: { backgroundColor: '#ef4444' },
  
  speedBadge: { position: 'absolute', bottom: 150, right: 16, backgroundColor: 'rgba(0,0,0,0.7)', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, zIndex: 60 }, 
  speedText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  
  drawPanel: { position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: '#fff', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 16, borderTopWidth: 1, borderTopColor: '#e2e8f0', zIndex: 100 },
  drawPanelHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  drawPanelTitle: { fontSize: 16, fontWeight: '600', color: '#0f172a' },
  drawPanelInfo: { fontSize: 13, color: '#64748b', marginBottom: 16 },
  drawPanelActions: { flexDirection: 'row', gap: 12 },
  drawPanelClear: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 12, borderRadius: 10, backgroundColor: '#fef2f2', gap: 8 },
  drawPanelClearText: { color: '#ef4444', fontWeight: '600' },
  drawPanelComplete: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 12, borderRadius: 10, backgroundColor: '#22c55e', gap: 8 },
  drawPanelCompleteDisabled: { opacity: 0.5 },
  drawPanelCompleteText: { color: '#fff', fontWeight: '600' },
  
  toast: {
    position: 'absolute',
    bottom: 100,
    left: 20,
    right: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 12,
    gap: 8,
    zIndex: 200,
    elevation: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  toastText: { color: '#fff', fontSize: 14, fontWeight: '500', flex: 1, textAlign: 'center' },
});