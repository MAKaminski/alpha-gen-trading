'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, Activity } from 'lucide-react';

interface ChartData {
  timestamp: string;
  vwap: number;
  ma9: number;
}

interface ChartProps {
  data: ChartData[];
  timeScale: string;
  onTimeScaleChange: (scale: string) => void;
}

export function Chart({ data, timeScale, onTimeScaleChange }: ChartProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    switch (timeScale) {
      case '1min':
        return date.toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit' 
        });
      case '5min':
      case '15min':
        return date.toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit' 
        });
      case '1hour':
      case '4hour':
        return date.toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit' 
        });
      case '1day':
        return date.toLocaleDateString('en-US', { 
          month: '2-digit', 
          day: '2-digit' 
        });
      default:
        return timestamp;
    }
  };

  const getScaleLabel = (scale: string) => {
    const labels = {
      '1min': '1 Minute',
      '5min': '5 Minutes',
      '15min': '15 Minutes',
      '1hour': '1 Hour',
      '4hour': '4 Hours',
      '1day': '1 Day'
    };
    return labels[scale as keyof typeof labels] || scale;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Live Chart - {getScaleLabel(timeScale)} Scale
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-96 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={formatTime}
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                stroke="#9CA3AF"
                fontSize={12}
                domain={['dataMin - 1', 'dataMax + 1']}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '6px',
                  color: '#F9FAFB'
                }}
                labelFormatter={(value) => `Time: ${formatTime(value)}`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="vwap"
                stroke="#4CAF50"
                strokeWidth={2}
                dot={false}
                name="VWAP"
              />
              <Line
                type="monotone"
                dataKey="ma9"
                stroke="#2196F3"
                strokeWidth={2}
                dot={false}
                name="MA9"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {data.length === 0 && (
          <div className="flex items-center justify-center h-96 text-gray-500">
            <div className="text-center">
              <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No data available</p>
              <p className="text-sm">Start streaming data to see the chart</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
