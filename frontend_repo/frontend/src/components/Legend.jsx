import React from 'react';

const Legend = () => {
  const ndviColors = [
    { color: '#FF0000', value: '-0.2', label: 'Very Low Vegetation' },
    { color: '#FFA500', value: '0.0', label: 'Low Vegetation' },
    { color: '#FFFF00', value: '0.2', label: 'Moderate Vegetation' },
    { color: '#90EE90', value: '0.4', label: 'Good Vegetation' },
    { color: '#008000', value: '0.6', label: 'High Vegetation' },
    { color: '#006400', value: '0.8', label: 'Very High Vegetation' }
  ];

  return (
    <div style={{
      position: 'absolute',
      bottom: '20px',
      right: '20px',
      background: 'white',
      padding: '15px',
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
      zIndex: 1000,
      minWidth: '220px',
      border: '1px solid #ccc'
    }}>
      <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: 'bold', color: '#333' }}>
        NDVI Values (Vegetation Health)
      </h4>
      <div style={{ fontSize: '12px' }}>
        {ndviColors.map((item, index) => (
          <div key={index} style={{ 
            display: 'flex', 
            alignItems: 'center', 
            marginBottom: '6px' 
          }}>
            <div style={{
              width: '20px',
              height: '20px',
              backgroundColor: item.color,
              marginRight: '8px',
              borderRadius: '2px',
              border: '1px solid #999'
            }}></div>
            <span style={{ fontWeight: 'bold', color: '#333' }}>{item.value}</span>
            <span style={{ marginLeft: '8px', color: '#666' }}>
              {item.label}
            </span>
          </div>
        ))}
      </div>
      <div style={{ 
        marginTop: '10px', 
        fontSize: '11px', 
        color: '#666',
        borderTop: '1px solid #eee',
        paddingTop: '8px'
      }}>
        <div>Data: Sentinel-2 (Last 12 months)</div>
        <div>Area: New York City</div>
      </div>
    </div>
  );
};

export default Legend;
