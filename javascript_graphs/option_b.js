import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';

const SimplifiedChart = () => {
  // Simple data for the three models
  const modelsData = [
    {
      name: "Model A",
      flagged: 12.5,  // % of content flagged
      found: 82.0,    // % of important items found
    },
    {
      name: "Model B",
      flagged: 16.2,
      found: 68.5,
    },
    {
      name: "Model C",
      flagged: 32.5,
      found: 54.0,
    }
  ];

  // Custom tooltip for simplicity
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const model = payload[0].payload;
      return (
        <div className="p-3 bg-white border border-gray-200 rounded shadow-sm">
          <p className="font-medium">{model.name}</p>
          <p>Flags {model.flagged}% of content</p>
          <p>Finds {model.found}% of important items</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Finding Important Content</h2>
      
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart
            margin={{ top: 20, right: 20, bottom: 40, left: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.6} />
            <XAxis 
              type="number" 
              dataKey="flagged" 
              name="flagged" 
              domain={[0, 40]} 
              label={{ value: 'Content Flagged (%)', position: 'bottom', offset: 10 }}
              tickCount={5}
            />
            <YAxis 
              type="number" 
              dataKey="found" 
              name="found" 
              domain={[0, 100]} 
              label={{ value: 'Important Items Found (%)', angle: -90, position: 'left' }}
              tickCount={6}
            />
            
            {/* Random guessing reference line */}
            <ReferenceLine 
              segment={[{ x: 0, y: 0 }, { x: 100, y: 100 }]} 
              stroke="#aaa" 
              strokeDasharray="5 5" 
              label={{ value: 'Random Selection', position: 'insideBottomRight' }} 
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            {/* Plot the models with simple coloring */}
            <Scatter
              data={modelsData}
              shape={(props) => {
                const { cx, cy } = props;
                // Color based on performance (green for Model A, yellow for B, red for C)
                let color;
                if (props.payload.name === "Model A") {
                  color = "#4CAF50";
                } else if (props.payload.name === "Model B") {
                  color = "#FFC107";
                } else {
                  color = "#FF5252";
                }
                
                return (
                  <g>
                    <circle cx={cx} cy={cy} r={8} fill={color} />
                    <text x={cx + 10} y={cy} textAnchor="start" fill="#333" style={{ fontSize: '12px' }}>
                      {props.payload.name}
                    </text>
                  </g>
                );
              }}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        <p><strong>Better models</strong> appear higher and to the left: they find more important items while flagging less content overall.</p>
        <p className="mt-2"><strong>For example:</strong> Model A flags just 12.5% of content but finds 82% of important items.</p>
      </div>
    </div>
  );
};

export default SimplifiedChart;