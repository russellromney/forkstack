# CI/CD Integration

Use forkstack to create ephemeral environments for pull requests, testing, and deployments.

## Overview

forkstack's instant environment creation makes it ideal for CI/CD pipelines:

- **Preview environments** - One environment per pull request
- **Integration testing** - Isolated test data per run
- **Staging** - Stable pre-production environments
- **Canary deployments** - Test with production data safely

## GitHub Actions

### Preview Environments per PR

```yaml
# .github/workflows/preview.yml
name: Preview Environment

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  create-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Turso CLI
        run: curl -sSfL https://get.tur.so/install.sh | bash

      - name: Install AWS CLI
        run: pip install awscli

      - name: Create preview environment
        env:
          TURSO_API_TOKEN: ${{ secrets.TURSO_API_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          ENV_NAME="pr-${{ github.event.pull_request.number }}"
          make envs-new $ENV_NAME

      - name: Deploy preview
        run: |
          ENV_NAME="pr-${{ github.event.pull_request.number }}"
          make envs-switch $ENV_NAME
          make deploy

      - name: Comment PR with preview URL
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Preview deployed: https://pr-${{ github.event.pull_request.number }}.preview.example.com'
            })
```

### Cleanup on PR Close

```yaml
# .github/workflows/cleanup.yml
name: Cleanup Preview

on:
  pull_request:
    types: [closed]

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Delete preview environment
        env:
          TURSO_API_TOKEN: ${{ secrets.TURSO_API_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          ENV_NAME="pr-${{ github.event.pull_request.number }}"
          make envs-delete $ENV_NAME
```

### Integration Tests

```yaml
# .github/workflows/test.yml
name: Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create test environment
        run: |
          ENV_NAME="test-${{ github.run_id }}"
          make envs-new $ENV_NAME
          make envs-switch $ENV_NAME

      - name: Run tests
        run: make test

      - name: Cleanup
        if: always()
        run: |
          ENV_NAME="test-${{ github.run_id }}"
          make envs-delete $ENV_NAME
```

## GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - preview
  - test
  - cleanup

create-preview:
  stage: preview
  script:
    - ENV_NAME="mr-${CI_MERGE_REQUEST_IID}"
    - make envs-new $ENV_NAME
    - make envs-switch $ENV_NAME
    - make deploy
  only:
    - merge_requests

run-tests:
  stage: test
  script:
    - ENV_NAME="test-${CI_PIPELINE_ID}"
    - make envs-new $ENV_NAME
    - make envs-switch $ENV_NAME
    - make test
    - make envs-delete $ENV_NAME

cleanup-preview:
  stage: cleanup
  script:
    - ENV_NAME="mr-${CI_MERGE_REQUEST_IID}"
    - make envs-delete $ENV_NAME
  when: manual
  only:
    - merge_requests
```

## Best Practices

### Environment Naming

Use consistent, identifiable names:

```bash
# Pull requests
pr-123
mr-456

# Test runs
test-abc123
ci-run-789

# Feature branches
feature-auth
feature-payments
```

### Automatic Cleanup

Always clean up environments to avoid accumulating unused resources:

```yaml
# Run cleanup even if tests fail
- name: Cleanup
  if: always()
  run: make envs-delete $ENV_NAME
```

### Secrets Management

Store credentials as CI secrets:

```yaml
env:
  TURSO_API_TOKEN: ${{ secrets.TURSO_API_TOKEN }}
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
```

### Parallel Testing

Create multiple environments for parallel test runs:

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - name: Create environment
        run: make envs-new test-${{ github.run_id }}-${{ matrix.shard }}

      - name: Run tests
        run: make test --shard ${{ matrix.shard }}
```

## Cost Considerations

forkstack's zero-copy approach keeps CI costs low:

| Approach | 100 PRs/month | Cost |
|----------|---------------|------|
| Traditional (full copies) | 100 x 10GB = 1TB | ~$23/month |
| forkstack (copy-on-write) | ~10GB total | ~$0.23/month |

Most CI environments write minimal data, so fork-on-write means near-zero additional storage costs.

## Troubleshooting

### Environment creation fails

Check CLI authentication:

```bash
turso auth whoami
aws sts get-caller-identity
```

### Cleanup not working

Ensure the environment exists before deleting:

```bash
# Check if exists first
if make envs-list | grep -q "$ENV_NAME"; then
  make envs-delete $ENV_NAME
fi
```

### Rate limits

Some services have rate limits on branch creation. For high-volume CI:

1. Reuse environments when possible
2. Add delays between operations
3. Contact your provider for higher limits
