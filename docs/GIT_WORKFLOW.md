# Git Workflow and Branching Strategy

## Branch Structure

### Main Branches
- **`main`**: Production-ready code, always deployable
- **`develop`**: Integration branch for features, staging environment

### Feature Branches
- **`feature/`**: New features and enhancements
  - `feature/trading-signals`
  - `feature/risk-management`
  - `feature/api-integration`

### Release Branches
- **`release/`**: Preparing new releases
  - `release/v1.0.0`
  - `release/v1.1.0`

### Hotfix Branches
- **`hotfix/`**: Critical production fixes
  - `hotfix/security-patch`
  - `hotfix/critical-bug`

## Commit Convention

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New features
- **fix**: Bug fixes
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Test additions or fixes
- **chore**: Build process or auxiliary tool changes

### Scopes
- **core**: Core application logic
- **api**: API integrations (Schwab, Polygon)
- **trading**: Trading logic and execution
- **data**: Data processing and ETL
- **ui**: User interface and visualization
- **config**: Configuration and settings
- **tests**: Test-related changes
- **docs**: Documentation
- **deps**: Dependencies

### Examples
```bash
feat(trading): add stop-loss functionality to trade manager

Implement dynamic stop-loss calculation based on entry credit.
Add configuration options for stop-loss multiples.
Include unit tests for stop-loss logic.

Closes #123
```

```bash
fix(api): resolve Schwab OAuth token refresh issue

Fix token refresh logic to handle expired tokens properly.
Add retry mechanism for failed token refresh attempts.
Update error handling to provide better user feedback.

Fixes #456
```

## Workflow Process

### 1. Feature Development
```bash
# Start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/trading-signals

# Make changes and commit
git add .
git commit -m "feat(trading): add VWAP/MA9 crossover detection"

# Push and create PR
git push origin feature/trading-signals
```

### 2. Pull Request Process
1. Create PR from feature branch to `develop`
2. Ensure all tests pass
3. Code review by team members
4. Address review feedback
5. Merge to `develop` when approved

### 3. Release Process
```bash
# Create release branch from develop
git checkout develop
git checkout -b release/v1.0.0

# Update version numbers, changelog
# Final testing and bug fixes

# Merge to main and develop
git checkout main
git merge release/v1.0.0
git tag v1.0.0

git checkout develop
git merge release/v1.0.0
```

### 4. Hotfix Process
```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/critical-bug

# Fix the issue
git commit -m "fix(core): resolve critical data processing bug"

# Merge to main and develop
git checkout main
git merge hotfix/critical-bug
git tag v1.0.1

git checkout develop
git merge hotfix/critical-bug
```

## Testing Requirements

### Before Merging
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Code coverage >= 80%
- [ ] Linting passes (ruff, mypy)
- [ ] Security checks pass

### Test Commands
```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit
pytest tests/integration
pytest tests/e2e

# Run with coverage
pytest --cov=src/alphagen --cov-report=html

# Run linting
ruff check src/ tests/
ruff format src/ tests/

# Run type checking
mypy src/alphagen
```

## Code Quality Standards

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Review Checklist
- [ ] Code follows project style guidelines
- [ ] Functions are well-documented
- [ ] Error handling is appropriate
- [ ] Tests cover new functionality
- [ ] No hardcoded values or secrets
- [ ] Performance considerations addressed
- [ ] Security implications considered

## Deployment Strategy

### Environments
- **Development**: `develop` branch
- **Staging**: `main` branch (pre-production)
- **Production**: Tagged releases from `main`

### Deployment Process
1. Code merged to `main`
2. CI/CD pipeline runs all tests
3. Build artifacts created
4. Automated deployment to staging
5. Manual approval for production
6. Production deployment with monitoring

## Emergency Procedures

### Critical Bug in Production
1. Create hotfix branch from `main`
2. Implement minimal fix
3. Test thoroughly
4. Deploy to production
5. Merge back to `develop`

### Rollback Procedure
1. Identify last known good commit
2. Create rollback branch
3. Revert problematic changes
4. Deploy rollback
5. Investigate root cause
6. Implement proper fix

## Branch Protection Rules

### Main Branch
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes to main

### Develop Branch
- Require pull request reviews
- Require status checks to pass
- Allow force pushes (for hotfixes)

## Best Practices

1. **Keep branches small and focused**
2. **Commit frequently with meaningful messages**
3. **Write tests before implementing features**
4. **Review code thoroughly before merging**
5. **Keep main branch always deployable**
6. **Use feature flags for incomplete features**
7. **Document breaking changes**
8. **Monitor production after deployments**
