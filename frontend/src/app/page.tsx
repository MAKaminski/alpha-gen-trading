'use client';

import { useState, useEffect } from 'react';
import { Controls } from '@/components/Controls';
import { Chart } from '@/components/Chart';
import { Console } from '@/components/Console';
import Navigation from '@/components/Navigation';
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
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto p-6 pt-12">
        <header className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                🚀 Alpha-Gen Debug Console
              </h1>
              <p className="text-gray-600">
                Real-time market data streaming and analysis
              </p>
            </div>
          </div>
          <div className="text-center mt-4">
            <a 
              href="/dashboard" 
              className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              📊 View Dashboard
            </a>
          </div>
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