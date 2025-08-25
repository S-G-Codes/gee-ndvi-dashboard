import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TimeSeriesChart = ({ data, point }) => {
  if (!data || data.length === 0) {
    return (
      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
        textAlign: 'center',
        color: '#666'
      }}>
        No time series data available for this location
      </div>
    );
  }

  return (
    <div style={{
      background: 'white',
      padding: '20px',
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
      minHeight: '300px'
    }}>
      <h3 style={{ margin: '0 0 15px 0', color: '#333' }}>
        NDVI Time Series
      </h3>
      <p style={{ margin: '0 0 15px 0', fontSize: '12px', color: '#666' }}>
        Location: {point?.lat?.toFixed(4)}°, {point?.lng?.toFixed(4)}°
      </p>
      
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 10 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            domain={[-0.2, 0.8]}
            tick={{ fontSize: 10 }}
            label={{ value: 'NDVI', angle: -90, position: 'insideLeft', fontSize: 12 }}
          />
          <Tooltip 
            formatter={(value) => [value, 'NDVI']}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Line 
            type="monotone" 
            dataKey="ndvi" 
            stroke="#4CAF50" 
            strokeWidth={2}
            dot={{ fill: '#4CAF50', strokeWidth: 2, r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div style={{ marginTop: '10px', fontSize: '11px', color: '#666' }}>
        Data points: {data.length} | Date range: {data[0]?.date} to {data[data.length - 1]?.date}
      </div>
    </div>
  );
};

export default TimeSeriesChart;
