'use client';

import { useState, useEffect } from 'react';
import { Controls } from '@/components/Controls';
import { Chart } from '@/components/Chart';
import { Console } from '@/components/Console';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useMarketData } from '@/hooks/useMarketData';

export default function Home() {
  const [streamDataActive, setStreamDataActive] = useState(false);
  const [viewChartActive, setViewChartActive] = useState(false);
  const [timeScale, setTimeScale] = useState('1min');
  
  const { isConnected, lastMessage, sendMessage } = useWebSocket();
  const { marketData, chartData, consoleLogs, startStreaming, stopStreaming } = useMarketData();

  const handleStreamToggle = (active: boolean) => {
    setStreamDataActive(active);
    if (active) {
      startStreaming();
    } else {
      stopStreaming();
    }
  };

  const handleChartToggle = (active: boolean) => {
    setViewChartActive(active);
  };

  const handleTimeScaleChange = (scale: string) => {
    setTimeScale(scale);
    sendMessage({ type: 'change_time_scale', scale });
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto p-6">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-center mb-2">
            🚀 Alpha-Gen Debug Console
          </h1>
          <p className="text-center text-gray-400">
            Real-time market data streaming and analysis
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Controls Panel */}
          <div className="space-y-6">
            <Controls
              streamDataActive={streamDataActive}
              viewChartActive={viewChartActive}
              timeScale={timeScale}
              isConnected={isConnected}
              onStreamToggle={handleStreamToggle}
              onChartToggle={handleChartToggle}
              onTimeScaleChange={handleTimeScaleChange}
            />

            {/* Console Output */}
            <Console logs={consoleLogs} />
          </div>

          {/* Chart Panel */}
          <div className="space-y-6">
            {viewChartActive && (
              <Chart
                data={chartData}
                timeScale={timeScale}
                onTimeScaleChange={handleTimeScaleChange}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}