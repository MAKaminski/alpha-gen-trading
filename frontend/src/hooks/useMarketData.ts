'use client';

import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
}

interface MarketData {
  symbol: string;
  price: number;
  timestamp: string;
}

interface ChartData {
  timestamp: string;
  vwap: number;
  ma9: number;
}

export function useMarketData() {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [consoleLogs, setConsoleLogs] = useState<LogEntry[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const { isConnected, lastMessage, sendMessage } = useWebSocket();

  // Process incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    switch (lastMessage.type) {
      case 'equity_tick':
        handleEquityTick(lastMessage.data);
        break;
      case 'option_quote':
        handleOptionQuote(lastMessage.data);
        break;
      case 'normalized_tick':
        handleNormalizedTick(lastMessage.data);
        break;
      case 'log':
        handleLogMessage(lastMessage.data);
        break;
      case 'stream_status':
        setIsStreaming(lastMessage.data.active);
        break;
      default:
        console.log('Unknown message type:', lastMessage.type);
    }
  }, [lastMessage]);

  const handleEquityTick = (data: any) => {
    const newData: MarketData = {
      symbol: data.symbol,
      price: data.price,
      timestamp: data.timestamp || new Date().toISOString(),
    };
    
    setMarketData(prev => [...prev.slice(-99), newData]);
    
    addLog('info', `Equity: ${data.symbol} = $${data.price.toFixed(2)}`);
  };

  const handleOptionQuote = (data: any) => {
    addLog('info', `Option: ${data.option_symbol} bid=$${data.bid.toFixed(2)} ask=$${data.ask.toFixed(2)}`);
  };

  const handleNormalizedTick = (data: any) => {
    const newChartData: ChartData = {
      timestamp: data.timestamp || new Date().toISOString(),
      vwap: data.equity?.session_vwap || 0,
      ma9: data.equity?.ma9 || 0,
    };
    
    setChartData(prev => [...prev.slice(-99), newChartData]);
    
    addLog('debug', `Normalized tick: VWAP=${newChartData.vwap.toFixed(2)}, MA9=${newChartData.ma9.toFixed(2)}`);
  };

  const handleLogMessage = (data: any) => {
    addLog(data.level || 'info', data.message);
  };

  const addLog = (level: LogEntry['level'], message: string) => {
    const logEntry: LogEntry = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      level,
      message,
    };
    
    setConsoleLogs(prev => [...prev.slice(-199), logEntry]);
  };

  const startStreaming = useCallback(() => {
    if (isConnected) {
      sendMessage({ type: 'start_stream' });
      addLog('info', 'Starting data stream...');
    } else {
      addLog('error', 'WebSocket not connected. Cannot start streaming.');
    }
  }, [isConnected, sendMessage]);

  const stopStreaming = useCallback(() => {
    if (isConnected) {
      sendMessage({ type: 'stop_stream' });
      addLog('info', 'Stopping data stream...');
    }
  }, [isConnected, sendMessage]);

  const clearLogs = useCallback(() => {
    setConsoleLogs([]);
    addLog('info', 'Console cleared');
  }, []);

  const exportLogs = useCallback(() => {
    const logsText = consoleLogs
      .map(log => `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}`)
      .join('\n');
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `alphagen-debug-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    addLog('info', 'Logs exported to file');
  }, [consoleLogs]);

  // Initialize with welcome message
  useEffect(() => {
    addLog('info', '🚀 Alpha-Gen Unified Debug Console started');
    addLog('info', '');
    addLog('info', '📊 Features:');
    addLog('info', '  • Check \'Stream Data\' to start receiving live market data');
    addLog('info', '  • Check \'View Chart\' to display live charts');
    addLog('info', '  • Use \'Setup OAuth\' to configure Schwab API access');
    addLog('info', '  • Use \'Clear Console\' to clear the output');
    addLog('info', '  • Use \'Export Logs\' to save console output to file');
    addLog('info', '');
    addLog('info', 'Ready for debugging! 🐛');
  }, []);

  return {
    marketData,
    chartData,
    consoleLogs,
    isStreaming,
    startStreaming,
    stopStreaming,
    clearLogs,
    exportLogs,
  };
}
