import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TrulySideBySideChart = () => {
  // Model data with simplified metrics
  const chartData = [
    {
      name: "Model A",
      efficiency: 98,     // % of flagged items that are important
      coverage: 82,       // % of important items found
      flagged: 12.5       // % of total content flagged
    },
    {
      name: "Model B",
      efficiency: 63,
      coverage: 69,
      flagged: 16.2
    },
    {
      name: "Model C",
      efficiency: 25,
      coverage: 54,
      flagged: 32.5
    }
  ];

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="p-3 bg-white border border-gray-200 rounded shadow-sm">
          <p className="font-medium">{data.name}</p>
          <p>Flags {data.flagged}% of all content</p>
          {payload[0].dataKey === 'efficiency' ? (
            <p><strong>{data.efficiency}%</strong> of flagged items are important</p>
          ) : (
            <p>Finds <strong>{data.coverage}%</strong> of important items</p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Model Performance Comparison</h2>
      
      <div className="flex flex-row space-x-6">
        {/* Efficiency Chart */}
        <div className="flex-1">
          <h3 className="text-base font-medium mb-1">Efficiency</h3>
          <p className="text-xs text-gray-500 mb-2">% of flagged items that are actually important</p>
          
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis 
                  domain={[0, 100]} 
                  tickCount={6}
                  label={{ value: '%', angle: -90, position: 'insideLeft' }} 
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="efficiency" 
                  fill="#4CAF50" 
                  radius={[4, 4, 0, 0]}
                  barSize={40}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-gray-600 mt-1 text-center">Higher is better - less wasted effort</p>
        </div>
        
        {/* Coverage Chart */}
        <div className="flex-1">
          <h3 className="text-base font-medium mb-1">Coverage</h3>
          <p className="text-xs text-gray-500 mb-2">% of important items found</p>
          
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis 
                  domain={[0, 100]} 
                  tickCount={6}
                  label={{ value: '%', angle: -90, position: 'insideLeft' }} 
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="coverage" 
                  fill="#2196F3" 
                  radius={[4, 4, 0, 0]}
                  barSize={40}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-gray-600 mt-1 text-center">Higher is better - fewer missed items</p>
        </div>
      </div>
      
      <div className="mt-4 text-sm text-gray-600 border-t pt-3">
        <p><strong>Model A</strong> is most efficient (98%) while still finding the most important items (82%).</p>
      </div>
    </div>
  );
};

export default TrulySideBySideChart;