'use client';

import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Play, Square, Settings, Download, Trash2 } from 'lucide-react';

interface ControlsProps {
  streamDataActive: boolean;
  viewChartActive: boolean;
  timeScale: string;
  isConnected: boolean;
  onStreamToggle: (active: boolean) => void;
  onChartToggle: (active: boolean) => void;
  onTimeScaleChange: (scale: string) => void;
}

export function Controls({
  streamDataActive,
  viewChartActive,
  timeScale,
  isConnected,
  onStreamToggle,
  onChartToggle,
  onTimeScaleChange,
}: ControlsProps) {
  const handleOAuthSetup = () => {
    // TODO: Implement OAuth setup
    console.log('OAuth setup clicked');
  };

  const handleClearConsole = () => {
    // TODO: Implement console clear
    console.log('Clear console clicked');
  };

  const handleExportLogs = () => {
    // TODO: Implement log export
    console.log('Export logs clicked');
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Alpha-Gen Debug Controls
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Main Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="stream-data"
              checked={streamDataActive}
              onCheckedChange={onStreamToggle}
            />
            <label htmlFor="stream-data" className="text-sm font-medium">
              Stream Data
            </label>
          </div>
          
          <div className="flex items-center space-x-2">
            <Checkbox
              id="view-chart"
              checked={viewChartActive}
              onCheckedChange={onChartToggle}
            />
            <label htmlFor="view-chart" className="text-sm font-medium">
              View Chart
            </label>
          </div>

          <Badge variant={isConnected ? "default" : "destructive"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
        </div>

        {/* Time Scale Control */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Time Scale:</label>
          <Select value={timeScale} onValueChange={onTimeScaleChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select time scale" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1min">1 Minute (60 points)</SelectItem>
              <SelectItem value="5min">5 Minutes (60 points)</SelectItem>
              <SelectItem value="15min">15 Minutes (60 points)</SelectItem>
              <SelectItem value="1hour">1 Hour (24 points)</SelectItem>
              <SelectItem value="4hour">4 Hours (18 points)</SelectItem>
              <SelectItem value="1day">1 Day (24 points)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleOAuthSetup}
            className="flex items-center gap-2"
          >
            <Settings className="h-4 w-4" />
            Setup OAuth
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearConsole}
            className="flex items-center gap-2"
          >
            <Trash2 className="h-4 w-4" />
            Clear Console
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportLogs}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Export Logs
          </Button>
        </div>

        {/* Status Information */}
        <div className="text-xs text-gray-400 space-y-1">
          <p>📊 Features:</p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Check 'Stream Data' to start receiving live market data</li>
            <li>Check 'View Chart' to display live charts</li>
            <li>Use 'Setup OAuth' to configure Schwab API access</li>
            <li>Use 'Clear Console' to clear the output</li>
            <li>Use 'Export Logs' to save console output to file</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
