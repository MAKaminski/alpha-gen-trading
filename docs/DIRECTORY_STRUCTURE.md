# Directory Structure Constraints

## Architecture Rule
**Only the following files are allowed at the project root level:**
- `pyproject.toml` - Project configuration and dependencies
- `pytest.ini` - Test configuration
- `README.md` - Project overview and quick start
- `.gitignore` - Git ignore rules
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

**All other files MUST be organized into appropriate subdirectories.**

## Directory Structure

```
alpha-gen/
├── pyproject.toml              # ✅ Project configuration
├── pytest.ini                  # ✅ Test configuration  
├── README.md                    # ✅ Project overview
├── .gitignore                   # ✅ Git ignore rules
├── .pre-commit-config.yaml      # ✅ Pre-commit hooks
│
├── src/                         # Source code
│   └── alphagen/               # Main package
│       ├── __init__.py
│       ├── app.py
│       ├── cli.py
│       ├── config.py
│       ├── core/               # Core business logic
│       ├── etl/                # Data processing
│       ├── market_data/        # Market data providers
│       ├── visualization/      # Charts and UI
│       └── ...
│
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   └── fixtures/               # Test data and utilities
│
├── scripts/                     # Executable scripts
│   ├── setup/                  # Setup and configuration scripts
│   │   ├── setup_schwab_oauth.py
│   │   ├── setup_real_schwab.py
│   │   └── get_new_token.py
│   ├── debug/                  # Debug and development scripts
│   │   ├── debug_app.py
│   │   ├── debug_cli.py
│   │   └── debug_chart_test.py
│   └── testing/                # Test execution scripts
│       ├── test_chart.py
│       ├── test_data_flow.py
│       └── test_simple_chart.py
│
├── config/                      # Configuration files
│   ├── schwab_token.json       # OAuth tokens
│   └── .gitmessage             # Git commit message template
│
├── docs/                        # Documentation
│   ├── setup/                  # Setup guides
│   │   ├── REAL_DATA_SETUP.md
│   │   └── DEBUG.md
│   ├── architecture/           # Architecture documentation
│   │   └── architecture.md
│   ├── GIT_WORKFLOW.md         # Git workflow guide
│   └── AGENT.md                # Agent documentation
│
├── deploy/                      # Deployment files
│   ├── README.md               # Deployment guide
│   ├── docker-compose.yml      # Docker composition
│   └── Dockerfile              # Docker image definition
│
├── data/                        # Data files
│   └── alpha_gen.db            # SQLite database
│
├── charts/                      # Generated chart files
│   └── *.png                   # Chart images
│
├── examples/                    # Example code and configurations
│   └── (future examples)
│
└── .github/                     # GitHub configuration
    └── workflows/              # CI/CD pipelines
        └── ci.yml
```

## File Organization Rules

### 1. Scripts Directory (`scripts/`)
- **Purpose**: Executable Python scripts that are not part of the main package
- **Subdirectories**:
  - `setup/`: Scripts for initial setup and configuration
  - `debug/`: Scripts for debugging and development
  - `testing/`: Scripts for running tests and test utilities

### 2. Config Directory (`config/`)
- **Purpose**: Configuration files, tokens, and templates
- **Contents**: OAuth tokens, Git templates, environment-specific configs

### 3. Docs Directory (`docs/`)
- **Purpose**: All documentation files
- **Subdirectories**:
  - `setup/`: Setup and installation guides
  - `architecture/`: Technical architecture documentation

### 4. Deploy Directory (`deploy/`)
- **Purpose**: Deployment-related files
- **Contents**: Docker files, deployment scripts, infrastructure configs

### 5. Data Directory (`data/`)
- **Purpose**: Runtime data files
- **Contents**: Databases, logs, temporary files

### 6. Charts Directory (`charts/`)
- **Purpose**: Generated chart images and visualizations
- **Contents**: PNG files, chart exports

## Enforcement

### Pre-commit Hook
A pre-commit hook will be added to enforce this structure:

```yaml
- repo: local
  hooks:
    - id: check-directory-structure
      name: Check directory structure
      entry: python scripts/testing/check_structure.py
      language: system
      pass_filenames: false
      always_run: true
```

### CI/CD Validation
The CI/CD pipeline will validate the directory structure before allowing merges.

## Migration Commands

To move files to their proper locations:

```bash
# Move setup scripts
mv setup_*.py scripts/setup/

# Move debug scripts  
mv debug_*.py scripts/debug/

# Move test scripts
mv test_*.py scripts/testing/

# Move documentation
mv *_SETUP.md docs/setup/
mv DEBUG.md docs/setup/
mv GIT_WORKFLOW.md docs/
mv AGENT.md docs/

# Move configuration files
mv schwab_token.json config/
mv .gitmessage config/

# Move deployment files
mv docker-compose.yml deploy/
mv Dockerfile deploy/

# Move data files
mkdir -p data
mv *.db data/
```

## Benefits

1. **Clarity**: Clear separation of concerns
2. **Maintainability**: Easy to find and organize files
3. **Scalability**: Structure supports growth
4. **Consistency**: Enforced organization across the project
5. **Professional**: Clean, enterprise-ready structure

## Exceptions

The only exceptions to this rule are:
- Files required by Python packaging (`pyproject.toml`, `pytest.ini`)
- Files required by Git (`.gitignore`, `.gitmessage`)
- Files required by development tools (`.pre-commit-config.yaml`)
- Project overview (`README.md`)

All other files MUST be organized into subdirectories.
