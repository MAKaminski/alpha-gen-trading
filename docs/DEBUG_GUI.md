# Alpha-Gen Debug GUI

The Alpha-Gen Debug GUI provides a user-friendly interface for monitoring live market data and viewing real-time charts during development and testing.

## Features

- **Stream Data Toggle**: Enable/disable live market data streaming
- **View Chart Toggle**: Show/hide live charts with VWAP vs MA9 analysis
- **Real-time Console**: Monitor data updates and system logs
- **Unified Interface**: All debugging tools in one beautiful console

## Usage

### Starting the Debug GUI

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the debug GUI
python -m alphagen debug
```

### Using the Interface

1. **Stream Data Checkbox**: 
   - Check to start receiving live market data from Schwab API
   - Uncheck to stop data streaming
   - Console will show real-time equity and option quotes

2. **View Chart Checkbox**:
   - Check to display live charts with VWAP vs MA9 analysis
   - Uncheck to hide charts
   - Charts show real-time price movements and crossover signals

3. **Console Output**:
   - Real-time data updates
   - System logs and error messages
   - Color-coded by log level (info, warning, error)

## Technical Details

### Architecture

- **GUI Framework**: tkinter (built into Python)
- **Async Integration**: Separate thread for async operations
- **Chart Engine**: matplotlib with live updates
- **Data Source**: Schwab API via OAuth client

### Components

- `DebugGUI`: Main GUI application class
- `LiveChart`: Real-time charting component
- `StreamCallbacks`: Data handling callbacks
- `Console Logging`: Real-time log display

### File Structure

```
src/alphagen/gui/
├── __init__.py
└── debug_app.py          # Main GUI application
```

## Development

The debug GUI integrates with the existing Alpha-Gen architecture:

- Uses the same market data providers
- Leverages existing chart components
- Maintains async compatibility
- Preserves all logging functionality

## Troubleshooting

### Common Issues

1. **GUI doesn't start**: Check that tkinter is available
2. **No data streaming**: Verify Schwab API credentials
3. **Charts not updating**: Ensure matplotlib is installed
4. **Async errors**: Check that the event loop is running

### Dependencies

- tkinter (usually included with Python)
- matplotlib (for charts)
- asyncio (for async operations)
- structlog (for logging)
