"use client";

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ChartDataPoint {
  time: string;
  vwap: number;
  ma9: number;
  signal?: string;
}

interface LiveChartProps {
  className?: string;
}

export default function LiveChart({ className = "" }: LiveChartProps) {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Generate mock data that mimics the application's VWAP/MA9 crossover strategy
  const generateMockData = () => {
    const now = new Date();
    const mockData: ChartDataPoint[] = [];
    const basePrice = 400; // QQQ base price
    
    for (let i = 59; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60000); // 1 minute intervals
      const timeStr = timestamp.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit' 
      });
      
      // Generate realistic VWAP and MA9 values with some correlation
      const randomFactor = Math.sin(i * 0.1) * 2 + Math.random() * 0.5;
      const vwap = basePrice + randomFactor;
      const ma9 = basePrice + randomFactor * 0.8 + Math.random() * 0.3;
      
      mockData.push({
        time: timeStr,
        vwap: Number(vwap.toFixed(2)),
        ma9: Number(ma9.toFixed(2))
      });
    }
    
    return mockData;
  };

  useEffect(() => {
    // Initialize with mock data
    setData(generateMockData());
    setIsConnected(true);
    setLastUpdate(new Date());

    // Simulate live updates every 5 seconds
    const interval = setInterval(() => {
      setData(prevData => {
        const newData = [...prevData];
        
        // Remove oldest point
        newData.shift();
        
        // Add new point
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit' 
        });
        
        const lastVwap = newData[newData.length - 1]?.vwap || 400;
        const lastMa9 = newData[newData.length - 1]?.ma9 || 400;
        
        // Generate new values with some momentum
        const vwapChange = (Math.random() - 0.5) * 0.5;
        const ma9Change = (Math.random() - 0.5) * 0.3;
        
        const newVwap = Number((lastVwap + vwapChange).toFixed(2));
        const newMa9 = Number((lastMa9 + ma9Change).toFixed(2));
        
        newData.push({
          time: timeStr,
          vwap: newVwap,
          ma9: newMa9
        });
        
        return newData;
      });
      
      setLastUpdate(new Date());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const formatTooltip = (value: number, name: string) => {
    return [`$${value.toFixed(2)}`, name === 'vwap' ? 'VWAP' : 'MA9'];
  };

  const formatXAxis = (tickItem: string) => {
    return tickItem;
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          QQQ VWAP vs MA9 - Live Chart
        </h3>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              Last update: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="time" 
              stroke="#666"
              fontSize={12}
              tickFormatter={formatXAxis}
            />
            <YAxis 
              stroke="#666"
              fontSize={12}
              domain={['dataMin - 1', 'dataMax + 1']}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip 
              formatter={formatTooltip}
              labelStyle={{ color: '#333' }}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e0e0e0',
                borderRadius: '6px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="vwap" 
              stroke="#4caf50" 
              strokeWidth={2}
              dot={false}
              name="VWAP"
            />
            <Line 
              type="monotone" 
              dataKey="ma9" 
              stroke="#2196f3" 
              strokeWidth={2}
              dot={false}
              name="MA9"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 text-xs text-gray-500">
        <p>📊 This chart simulates the live VWAP/MA9 crossover strategy data from Alpha-Gen</p>
        <p>🔄 Updates every 5 seconds with mock market data</p>
        <p>📈 Green line: VWAP (Volume Weighted Average Price)</p>
        <p>📈 Blue line: MA9 (9-period Moving Average)</p>
      </div>
    </div>
  );
}
