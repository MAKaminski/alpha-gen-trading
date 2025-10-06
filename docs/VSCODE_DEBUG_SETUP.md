# VS Code Debug Configuration

This document describes the VS Code launch configurations available for the Alpha-Gen project.

## Available Launch Configurations

### 🐛 Run Alpha-Gen (Unified GUI)
- **Purpose**: Launch the main debug GUI application
- **Module**: `src.alphagen`
- **Arguments**: `["debug"]`
- **Environment**: PYTHONPATH includes both root and src directories
- **Usage**: Press F5 or click play button in VS Code

### 🧪 Run Test Suite [All Tests - Unit, Integration E2E]
- **Purpose**: Run the complete test suite with coverage reporting
- **Module**: `pytest`
- **Arguments**: All test directories with coverage settings
- **Coverage**: 80% minimum threshold
- **Reports**: Terminal, HTML, and XML coverage reports
- **Usage**: Select from debug dropdown and run

### 🚀 Run Backend API
- **Purpose**: Launch the FastAPI backend server
- **Program**: `backend/main.py`
- **Environment**: PYTHONPATH includes both root and src directories
- **Usage**: For API development and testing

### 🔧 Run Frontend Dev Server
- **Purpose**: Start the Next.js frontend development server
- **Type**: Node.js
- **Runtime**: npm run dev
- **Working Directory**: frontend/
- **Usage**: For frontend development

## Configuration Details

### PYTHONPATH Setup
All Python configurations use:
```json
"env": {
    "PYTHONPATH": "${workspaceFolder}:${workspaceFolder}/src"
}
```

This ensures:
- Root directory imports work
- Source package imports work
- Module resolution is consistent

### Test Configuration
The test configuration includes:
- All test directories (`tests/`)
- Verbose output (`-v`)
- Short traceback (`--tb=short`)
- Coverage reporting for `src/alphagen`
- 80% minimum coverage threshold
- HTML coverage report in `htmlcov/`

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Ensure PYTHONPATH is set correctly
   - Check that you're running from the project root
   - Verify the module path in launch.json

2. **Test failures**
   - Check that all dependencies are installed
   - Ensure test data is available
   - Verify API credentials if tests require them

3. **Coverage below threshold**
   - Run tests to see which files need coverage
   - Add missing test cases
   - Check that all code paths are tested

### Debug Tips

1. **Setting breakpoints**: Click in the gutter next to line numbers
2. **Variable inspection**: Hover over variables during debugging
3. **Console access**: Use the Debug Console for interactive debugging
4. **Step through code**: Use F10 (step over) and F11 (step into)

## File Structure

```
.vscode/
└── launch.json          # VS Code launch configurations

docs/
└── VSCODE_DEBUG_SETUP.md  # This documentation
```

## Related Documentation

- [DEBUG_GUI.md](./DEBUG_GUI.md) - Debug GUI usage
- [TEST_COVERAGE_VISUALIZATION.md](./TEST_COVERAGE_VISUALIZATION.md) - Test coverage details
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Deployment information
