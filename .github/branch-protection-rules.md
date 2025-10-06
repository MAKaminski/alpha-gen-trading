# Branch Protection Rules for Main Branch

## Required Status Checks
The following status checks must pass before merging to main:

1. **pre-merge-checks** - Comprehensive test suite including:
   - Unit tests (80%+ coverage)
   - Integration tests (80%+ coverage) 
   - E2E tests (80%+ coverage)
   - Linting (ruff check + format)
   - Type checking (mypy)
   - Security scanning (safety + bandit)

## Branch Protection Settings

### Required Status Checks
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Require linear history
- ✅ Require conversation resolution before merging

### Required Status Checks (Specific)
- `pre-merge-checks` - Must pass
- `test` - Must pass (from CI/CD Pipeline)
- `security` - Must pass (from CI/CD Pipeline)

### Restriction Settings
- ✅ Restrict pushes that create files larger than 100MB
- ✅ Require signed commits
- ✅ Require deployments to succeed before merging
- ✅ Lock branch (prevent force pushes)

### Admin Override
- ❌ Allow force pushes (disabled)
- ❌ Allow deletions (disabled)
- ✅ Include administrators (admins must follow rules)

## Implementation

To apply these rules via GitHub CLI:

```bash
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["pre-merge-checks","test","security"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
  --field restrictions='{"users":[],"teams":[],"apps":[]}' \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

## Manual Configuration

1. Go to repository Settings → Branches
2. Add rule for `main` branch
3. Enable "Require status checks to pass before merging"
4. Select required status checks: `pre-merge-checks`, `test`, `security`
5. Enable "Require branches to be up to date before merging"
6. Enable "Require linear history"
7. Enable "Require conversation resolution before merging"
8. Enable "Restrict pushes that create files larger than 100MB"
9. Enable "Require signed commits"
10. Enable "Include administrators"
11. Disable "Allow force pushes"
12. Disable "Allow deletions"
