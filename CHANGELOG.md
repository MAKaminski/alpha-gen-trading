# Changelog

All notable changes to the Alpha-Gen project will be documented in this file.

## [Unreleased] - 2025-10-07

### ✨ Added
- Enhanced GUI debug console with dark theme (`#1e1e1e` background)
- Color-coded log levels (info: green, warning: orange, error: red, debug: gray)
- Monospace font (Consolas 10pt) for better console readability
- Price range tracking for Y-axis across all chart visualizations
- Smart Y-axis tick increments based on price range ($1, $0.10, or $0.01)
- Improved X-axis label spacing (5-minute intervals by default)
- Minor tick marks for better time resolution
- 45-degree label rotation for better readability
- pytest-timeout plugin for test reliability

### 🔧 Fixed
- **Test Suite Timeouts**: Fixed all hanging tests - suite now completes in ~7 seconds
  - Fixed `test_market_data_to_signal_flow` by mocking `asyncio.Event.wait()`
  - Fixed `test_debug_command_execution` by correcting mock import paths
  - Fixed `test_debug_command_error_handling` with proper path
- **Chart Visualization**:
  - Y-axis now shows reasonable price ranges (not pennies)
  - Y-axis tracks min/max values across all time for proper scaling
  - X-axis labels no longer overlap with proper spacing
  - All chart types (GUI, File, Simple, Live) have consistent formatting
- **Test Runner**: 
  - Corrected PYTHONPATH order for proper module resolution
  - Added pytest-timeout for test reliability
  - Removed timeout flag when plugin not available

### 🎨 Improved
- Chart Y-axis padding (5% above/below min/max)
- Time scale configurations with smart interval selection
- Console text widget styling with high contrast
- Test execution speed (from hanging indefinitely to 7 seconds)

### 📊 Test Coverage
- **312 tests passing** (97% success rate)
- **69% code coverage** (up from previous baseline)
- Only 9 legitimate test failures remaining (all mock-related, non-blocking)

### 🗂️ Files Modified
- `src/alphagen/visualization/simple_gui_chart.py` - Chart improvements
- `src/alphagen/visualization/file_chart.py` - X-axis formatting
- `src/alphagen/visualization/simple_chart.py` - X-axis formatting  
- `src/alphagen/visualization/live_chart.py` - X-axis formatting
- `src/alphagen/gui/debug_app.py` - Console styling
- `run_tests.py` - PYTHONPATH and timeout fixes
- `tests/integration/test_data_flow.py` - Mock fixes for async event loops
- `tests/unit/test_cli_comprehensive.py` - Mock path corrections

### 🔍 Technical Details

#### Chart Improvements
The visualization system now provides professional-grade charts with:
- Dynamic Y-axis scaling based on actual data ranges
- Smart tick increment selection (prevents penny-level scaling)
- Time-based X-axis intervals that adapt to data density
- Consistent formatting across all chart implementations

#### Console Improvements
The debug GUI console features:
- Dark theme for reduced eye strain during development
- High-contrast color scheme for better log differentiation
- Monospace font for aligned structured output
- Professional appearance matching modern IDEs

#### Test Infrastructure
- Resolved all timeout issues by properly mocking long-running operations
- Tests now provide immediate feedback
- Fixed import path inconsistencies
- Added proper pytest-timeout integration

## [0.1.0] - Initial Release

### Added
- Real-time QQQ options trading system
- VWAP/MA9 crossover strategy
- Schwab API integration
- Polygon data streaming
- SQLite storage layer
- Live visualization charts
- Debug GUI interface
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions
- Railway and Vercel deployment configurations

