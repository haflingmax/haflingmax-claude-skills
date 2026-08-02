# CI/CD Pipeline

Every project should have a CI pipeline. When setting up a project or adding testing/Storybook,
check if `.github/workflows/` exists. If not, create the pipeline.

## Recommended GitHub Actions Pipeline

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run test -- --coverage
      - uses: codecov/codecov-action@v4
        if: always()

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run build

  storybook:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run build-storybook
        env:
          NODE_OPTIONS: "--max-old-space-size=4096"

  e2e:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run build
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: playwright-report/
```

## Pipeline Stages (Parallel Where Possible)

| Stage | Job | Blocks deploy? |
|-------|-----|----------------|
| Quality | lint, typecheck | Yes |
| Testing | unit tests, Storybook build | Yes |
| Build | app build | Yes |
| E2E | Playwright (after build) | Yes |
| Visual | Chromatic (optional) | No (advisory) |
| Docker | build + push (main only) | -- |
| Deploy | preview on PR, prod on main | -- |

## Rules
- `concurrency.cancel-in-progress: true` — don't waste runners on superseded commits.
- Cache `node_modules` via `actions/setup-node` with `cache: npm`.
- Storybook build needs `NODE_OPTIONS="--max-old-space-size=4096"`.
- Playwright: use `npx playwright install --with-deps`, NOT the deprecated `microsoft/playwright-github-action`.
- Upload test reports as artifacts (`playwright-report/`, `coverage/`).
- Docker build+push only on merge to main, gated by all quality checks passing.

## Detection Rule

During project detection, also check:
- `.github/workflows/` — CI pipeline exists?
- `Dockerfile` / `docker-compose.yml` — Docker setup exists?

If tests or Storybook are added but no CI exists, proactively suggest creating the pipeline.
