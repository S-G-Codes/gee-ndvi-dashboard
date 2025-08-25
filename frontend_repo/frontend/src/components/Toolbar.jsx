import React from 'react';

const Toolbar = ({ 
  selectedAOI, 
  onAOIChange, 
  baseMapType, 
  onBaseMapChange, 
  onExportData,
  showTimeSeries,
  onToggleTimeSeries,
  showStats,
  onToggleStats
}) => {
  const aois = [
    { value: 'nyc', label: 'New York City' },
    { value: 'amazon', label: 'Amazon Rainforest' },
    { value: 'sahara', label: 'Sahara Desert' }
  ];

  const baseMaps = [
    { value: 'osm', label: 'OpenStreetMap' },
    { value: 'satellite', label: 'Satellite' }
  ];

  return (
    <div style={{
      position: 'absolute',
      top: '80px',
      left: '10px',
      background: 'white',
      padding: '15px',
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
      zIndex: 1000,
      minWidth: '250px',
      border: '1px solid #ccc'
    }}>
      <h4 style={{ margin: '0 0 15px 0', fontSize: '14px', fontWeight: 'bold', color: '#333' }}>
        Dashboard Controls
      </h4>
      
      {/* AOI Selection */}
      <div style={{ marginBottom: '15px' }}>
        <label style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '5px' }}>
          Area of Interest:
        </label>
        <select 
          value={selectedAOI} 
          onChange={(e) => onAOIChange(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ccc',
            fontSize: '12px'
          }}
        >
          {aois.map(aoi => (
            <option key={aoi.value} value={aoi.value}>
              {aoi.label}
            </option>
          ))}
        </select>
      </div>

      {/* Base Map Toggle */}
      <div style={{ marginBottom: '15px' }}>
        <label style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '5px' }}>
          Base Map:
        </label>
        <div style={{ display: 'flex', gap: '5px' }}>
          {baseMaps.map(map => (
            <button
              key={map.value}
              onClick={() => onBaseMapChange(map.value)}
              style={{
                flex: 1,
                padding: '8px',
                backgroundColor: baseMapType === map.value ? '#4CAF50' : '#f5f5f5',
                color: baseMapType === map.value ? 'white' : '#333',
                border: '1px solid #ccc',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '11px'
              }}
            >
              {map.label}
            </button>
          ))}
        </div>
      </div>

      {/* Analysis Layer Toggle */}
      <div style={{ marginBottom: '15px' }}>
        <label style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '5px' }}>
          Analysis Layers:
        </label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <button
            onClick={onToggleTimeSeries}
            style={{
              padding: '8px',
              backgroundColor: showTimeSeries ? '#2196F3' : '#f5f5f5',
              color: showTimeSeries ? 'white' : '#333',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '11px'
            }}
          >
            {showTimeSeries ? 'Hide' : 'Show'} Time Series
          </button>
          <button
            onClick={onToggleStats}
            style={{
              padding: '8px',
              backgroundColor: showStats ? '#FF9800' : '#f5f5f5',
              color: showStats ? 'white' : '#333',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '11px'
            }}
          >
            {showStats ? 'Hide' : 'Show'} Statistics
          </button>
        </div>
      </div>

      {/* Export Button */}
      <div style={{ marginBottom: '15px' }}>
        <button
          onClick={onExportData}
          style={{
            width: '100%',
            padding: '10px',
            backgroundColor: '#9C27B0',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
        >
          📊 Export Report
        </button>
      </div>

      {/* Instructions */}
      <div style={{ fontSize: '11px', color: '#666', borderTop: '1px solid #eee', paddingTop: '10px' }}>
        <div style={{ marginBottom: '5px' }}>💡 Instructions:</div>
        <div>• Click on map to see pixel values</div>
        <div>• Use controls to switch AOIs</div>
        <div>• Toggle layers for analysis</div>
      </div>
    </div>
  );
};

export default Toolbar;
