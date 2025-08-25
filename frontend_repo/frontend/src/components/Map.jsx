import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import Legend from './Legend';
import Toolbar from './Toolbar';
import TimeSeriesChart from './TimeSeriesChart';

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// API base URL from env
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const MapComponent = () => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const ndviLayerRef = useRef(null);
  const baseLayerRef = useRef(null);
  
  // State management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataInfo, setDataInfo] = useState(null);
  const [ndviVisible, setNdviVisible] = useState(true);
  const [opacity, setOpacity] = useState(0.9);
  
  // GIS Assignment features
  const [selectedAOI, setSelectedAOI] = useState('nyc');
  const [baseMapType, setBaseMapType] = useState('osm');
  const [showTimeSeries, setShowTimeSeries] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [timeSeriesData, setTimeSeriesData] = useState(null);
  const [pixelStats, setPixelStats] = useState(null);
  const [clickedPoint, setClickedPoint] = useState(null);

  // Initialize map
 useEffect(() => {
    if (!mapRef.current) return;

    // Clean up existing map
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const timer = setTimeout(() => {
      try {
        // Initialize map
  const map = L.map(mapRef.current, {
    zoomControl: true,
    minZoom: 3,
          maxZoom: 19,
          center: [40.7128, -74.006],
          zoom: 10
        });

        mapInstanceRef.current = map;

        // Add base layer
        const baseLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
        });
        baseLayer.addTo(map);
        baseLayerRef.current = baseLayer;

        // Load initial NDVI data
        loadNDVIData();

        // Add click handler
        map.on('click', handleMapClick);

      } catch (err) {
        console.error("Error initializing map:", err);
        setError("Failed to initialize map");
        setLoading(false);
      }
    }, 100);

  return () => {
      clearTimeout(timer);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
  };
}, []);

  // Load NDVI data
  const loadNDVIData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE}/aoi/${selectedAOI}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      if (data.tile_url && mapInstanceRef.current) {
        // Remove existing NDVI layer
        if (ndviLayerRef.current) {
          ndviLayerRef.current.remove();
        }

        // Add new NDVI layer
        const ndviTileLayer = L.tileLayer(data.tile_url, {
          attribution: 'NDVI Data from Google Earth Engine',
          opacity: opacity,
          zIndex: 1000
        });
        
        ndviLayerRef.current = ndviTileLayer;
        ndviTileLayer.addTo(mapInstanceRef.current);
        setDataInfo(data);

        // Fit bounds based on AOI
        const bounds = getAOIBounds(selectedAOI);
        mapInstanceRef.current.fitBounds(bounds);
      }
    } catch (err) {
      console.error("Error loading NDVI data:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle map click
  const handleMapClick = async (e) => {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;
    setClickedPoint({ lat, lng });

    // Show popup with coordinates
    const popup = L.popup()
      .setLatLng(e.latlng)
      .setContent(`
        <div style="min-width: 200px;">
          <h4 style="margin: 0 0 8px 0; color: #333;">Location Info</h4>
          <p style="margin: 4px 0; font-size: 12px;">
            <strong>Latitude:</strong> ${lat.toFixed(4)}°
          </p>
          <p style="margin: 4px 0; font-size: 12px;">
            <strong>Longitude:</strong> ${lng.toFixed(4)}°
          </p>
          <p style="margin: 4px 0; font-size: 12px; color: #666;">
            Loading pixel data...
          </p>
        </div>
      `)
      .openOn(mapInstanceRef.current);

    // Load pixel statistics
    try {
      const statsResponse = await fetch(`${API_BASE}/stats/${lat}/${lng}`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        if (!statsData.error) {
          setPixelStats(statsData);
          
          // Update popup with stats
          popup.setContent(`
            <div style="min-width: 200px;">
              <h4 style="margin: 0 0 8px 0; color: #333;">Pixel Statistics</h4>
              <p style="margin: 4px 0; font-size: 12px;">
                <strong>Mean NDVI:</strong> ${statsData.statistics.mean}
              </p>
              <p style="margin: 4px 0; font-size: 12px;">
                <strong>Min NDVI:</strong> ${statsData.statistics.min}
              </p>
              <p style="margin: 4px 0; font-size: 12px;">
                <strong>Max NDVI:</strong> ${statsData.statistics.max}
              </p>
              <p style="margin: 4px 0; font-size: 12px;">
                <strong>Std Dev:</strong> ${statsData.statistics.std_dev}
              </p>
            </div>
          `);
        }
      }
    } catch (err) {
      console.error("Error loading pixel stats:", err);
    }

    // Load time series if enabled
    if (showTimeSeries) {
      loadTimeSeriesData(lat, lng);
    }
  };

  // Load time series data
  const loadTimeSeriesData = async (lat, lng) => {
    try {
      const response = await fetch(`${API_BASE}/time-series/${lat}/${lng}`);
      if (response.ok) {
        const data = await response.json();
        if (!data.error) {
          setTimeSeriesData(data);
        }
      }
    } catch (err) {
      console.error("Error loading time series:", err);
    }
  };

  // Get AOI bounds
  const getAOIBounds = (aoi) => {
    const bounds = {
      nyc: [[40.5, -74.3], [40.9, -73.7]],
      amazon: [[-10.0, -70.0], [5.0, -50.0]],
      sahara: [[15.0, -10.0], [35.0, 30.0]]
    };
    return bounds[aoi] || bounds.nyc;
  };

  // Handle AOI change
  const handleAOIChange = (newAOI) => {
    setSelectedAOI(newAOI);
    setTimeSeriesData(null);
    setPixelStats(null);
    setClickedPoint(null);
  };

  // Handle base map change
  const handleBaseMapChange = (newBaseMap) => {
    setBaseMapType(newBaseMap);
    
    if (mapInstanceRef.current && baseLayerRef.current) {
      baseLayerRef.current.remove();
      
      let newBaseLayer;
      if (newBaseMap === 'satellite') {
        newBaseLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
          attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        });
      } else {
        newBaseLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenStreetMap contributors'
        });
      }
      
      newBaseLayer.addTo(mapInstanceRef.current);
      baseLayerRef.current = newBaseLayer;
    }
  };

  // Handle opacity change
  useEffect(() => {
    if (ndviLayerRef.current) {
      ndviLayerRef.current.setOpacity(opacity);
    }
  }, [opacity]);

  // Handle NDVI layer toggle
  const toggleNdviLayer = () => {
    if (ndviLayerRef.current) {
      if (ndviVisible) {
        ndviLayerRef.current.remove();
      } else {
        ndviLayerRef.current.addTo(mapInstanceRef.current);
      }
      setNdviVisible(!ndviVisible);
    }
  };

  // Handle time series toggle
  const handleToggleTimeSeries = () => {
    setShowTimeSeries(!showTimeSeries);
    if (!showTimeSeries && clickedPoint) {
      loadTimeSeriesData(clickedPoint.lat, clickedPoint.lng);
    }
  };

  // Handle stats toggle
  const handleToggleStats = () => {
    setShowStats(!showStats);
  };

  // Export data
  const handleExportData = () => {
    const exportData = {
      aoi: selectedAOI,
      timestamp: new Date().toISOString(),
      data: dataInfo,
      pixelStats: pixelStats,
      timeSeries: timeSeriesData
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ndvi-dashboard-${selectedAOI}-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Reload data when AOI changes
  useEffect(() => {
    if (mapInstanceRef.current) {
      loadNDVIData();
    }
  }, [selectedAOI]);

  return (
    <div style={{ position: 'relative', height: '100vh', width: '100vw' }}>
      {/* Title Banner */}
      <div style={{
        position: 'absolute',
        top: '0',
        left: '0',
        right: '0',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '10px 20px',
        zIndex: 1001,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ margin: '0', fontSize: '24px', fontWeight: 'bold' }}>
          🌱 GEE NDVI Dashboard
        </h1>
        <p style={{ margin: '5px 0 0 0', fontSize: '14px', opacity: 0.9 }}>
          Interactive Vegetation Health Analysis using Google Earth Engine & Sentinel-2 Data
        </p>
      </div>

    <div
      ref={mapRef}
      id="map"
        style={{ height: '100%', width: '100%', marginTop: '60px' }}
      />
      
      {/* Toolbar */}
      <Toolbar
        selectedAOI={selectedAOI}
        onAOIChange={handleAOIChange}
        baseMapType={baseMapType}
        onBaseMapChange={handleBaseMapChange}
        onExportData={handleExportData}
        showTimeSeries={showTimeSeries}
        onToggleTimeSeries={handleToggleTimeSeries}
        showStats={showStats}
        onToggleStats={handleToggleStats}
      />

      {/* NDVI Controls */}
      <div style={{
        position: 'absolute',
        top: '80px',
        left: '280px',
        background: 'white',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
        zIndex: 1000,
        minWidth: '200px',
        border: '1px solid #ccc'
      }}>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: 'bold', color: '#333' }}>
          NDVI Controls
        </h4>
        
        {/* Toggle Button */}
        <div style={{ marginBottom: '10px' }}>
          <button 
            onClick={toggleNdviLayer}
            style={{
              padding: '8px 12px',
              backgroundColor: ndviVisible ? '#4CAF50' : '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            {ndviVisible ? 'Hide NDVI' : 'Show NDVI'}
          </button>
        </div>

        {/* Opacity Slider */}
        <div style={{ marginBottom: '10px' }}>
          <label style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '5px' }}>
            Opacity: {Math.round(opacity * 100)}%
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={opacity}
            onChange={(e) => setOpacity(parseFloat(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>

        {/* Data Info */}
        {dataInfo && (
          <div style={{ fontSize: '11px', color: '#666', borderTop: '1px solid #eee', paddingTop: '8px' }}>
            <div>AOI: {dataInfo.aoi_name}</div>
            <div>Images: {dataInfo.image_count}</div>
            <div>Date: {dataInfo.date_range.start} to {dataInfo.date_range.end}</div>
          </div>
        )}
      </div>

      {/* Time Series Chart */}
      {showTimeSeries && timeSeriesData && (
        <div style={{
          position: 'absolute',
          top: '80px',
          right: '20px',
          width: '400px',
          zIndex: 1000
        }}>
          <TimeSeriesChart 
            data={timeSeriesData.time_series} 
            point={timeSeriesData.point}
          />
        </div>
      )}

      {/* Pixel Statistics */}
      {showStats && pixelStats && (
        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '20px',
          background: 'white',
          padding: '15px',
          borderRadius: '8px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
          zIndex: 1000,
          minWidth: '250px',
          border: '1px solid #ccc'
        }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: 'bold', color: '#333' }}>
            Pixel Statistics
          </h4>
          <div style={{ fontSize: '12px' }}>
            <div><strong>Location:</strong> {pixelStats.point.lat.toFixed(4)}°, {pixelStats.point.lng.toFixed(4)}°</div>
            <div><strong>Mean NDVI:</strong> {pixelStats.statistics.mean}</div>
            <div><strong>Min NDVI:</strong> {pixelStats.statistics.min}</div>
            <div><strong>Max NDVI:</strong> {pixelStats.statistics.max}</div>
            <div><strong>Std Dev:</strong> {pixelStats.statistics.std_dev}</div>
            <div><strong>Images:</strong> {pixelStats.image_count}</div>
          </div>
        </div>
      )}

      {/* Loading and Error Messages */}
      {loading && (
        <div style={{
          position: 'absolute',
          top: '80px',
          left: '500px',
          background: 'white',
          padding: '10px',
          borderRadius: '5px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
          zIndex: 1000
        }}>
          Loading NDVI data...
        </div>
      )}
      
      {error && (
        <div style={{
          position: 'absolute',
          top: '80px',
          left: '500px',
          background: '#ffebee',
          color: '#c62828',
          padding: '10px',
          borderRadius: '5px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
          zIndex: 1000
        }}>
          Error: {error}
        </div>
      )}

      {/* Legend */}
      {dataInfo && !error && <Legend />}
    </div>
  );
};

export default MapComponent;
