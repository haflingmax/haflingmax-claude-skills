# Tooling: ESLint, Prettier, Pre-commit, IDE

Shared toolchain configuration for team consistency.

---

## ESLint Configuration

```js
// eslint.config.mjs (flat config, ESLint 9+)
import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import reactHooks from 'eslint-plugin-react-hooks'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import importPlugin from 'eslint-plugin-import'

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.strict,
  {
    plugins: {
      'react-hooks': reactHooks,
      'jsx-a11y': jsxA11y,
      'import': importPlugin,
    },
    rules: {
      // TypeScript
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports' }],
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],

      // React Hooks
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',

      // Accessibility
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/anchor-is-valid': 'error',
      'jsx-a11y/click-events-have-key-events': 'error',
      'jsx-a11y/no-static-element-interactions': 'error',
      'jsx-a11y/label-has-associated-control': 'error',

      // Import ordering
      'import/order': ['error', {
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'type'],
        pathGroups: [
          { pattern: 'react', group: 'builtin', position: 'before' },
          { pattern: 'next/**', group: 'builtin', position: 'before' },
          { pattern: '@/**', group: 'internal', position: 'before' },
        ],
        pathGroupsExcludedImportTypes: ['type'],
        'newlines-between': 'always',
        alphabetize: { order: 'asc' },
      }],
      'import/no-cycle': 'error',

      // Code quality
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'complexity': ['warn', 15],
      'no-magic-numbers': ['warn', {
        ignore: [0, 1, -1, 2, 100, 200, 201, 204, 400, 401, 403, 404, 500],
        ignoreArrayIndexes: true,
        ignoreDefaultValues: true,
      }],
    },
  },
  {
    // Disable some rules for test files
    files: ['**/*.test.{ts,tsx}', '**/*.stories.{ts,tsx}'],
    rules: {
      'no-magic-numbers': 'off',
    },
  }
)
```

### Import Order (enforced by ESLint)

```tsx
// 1. React / Next.js built-ins
import { useState } from 'react'
import Image from 'next/image'

// 2. Third-party libraries
import { z } from 'zod'
import { cva } from 'class-variance-authority'

// 3. Internal aliases (@/)
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

// 4. Relative imports
import { useProductCard } from './useProductCard'
import styles from './ProductCard.module.css'

// 5. Type-only imports (last, or inline with { type X })
import type { Product } from '@/entities/product'
```

---

## Prettier Configuration

```json
// .prettierrc
{
  "printWidth": 100,
  "singleQuote": true,
  "trailingComma": "all",
  "semi": false,
  "tabWidth": 2,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

`prettier-plugin-tailwindcss` auto-sorts Tailwind classes in canonical order.

---

## Pre-commit Hooks (Husky + lint-staged)

```bash
# Install
npm install -D husky lint-staged
npx husky init
```

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,css}": [
      "prettier --write"
    ]
  }
}
```

```bash
# .husky/pre-commit
npx lint-staged
```

```bash
# .husky/pre-push (optional — heavier checks)
npx tsc --noEmit
```

### Conventional Commits (commitlint)

```bash
npm install -D @commitlint/cli @commitlint/config-conventional
```

```js
// commitlint.config.js
export default { extends: ['@commitlint/config-conventional'] }
```

```bash
# .husky/commit-msg
npx --no -- commitlint --edit $1
```

**Commit format:** `type(scope): description`

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes nor adds |
| `style` | Formatting, white-space |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `chore` | Build, deps, config changes |
| `perf` | Performance improvement |

Example: `feat(cart): add quantity selector to cart items`

---

## VS Code Workspace Settings

```json
// .vscode/settings.json (commit to repo)
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "typescript.preferences.importModuleSpecifier": "non-relative",
  "typescript.tsdk": "node_modules/typescript/lib",
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["cn\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ]
}
```

```json
// .vscode/extensions.json (recommend to team)
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "yoavbls.pretty-ts-errors"
  ]
}
```

---

## Branch Naming

Pattern: `type/ticket-description`

```
feat/PROJ-123-add-checkout-flow
fix/PROJ-456-cart-total-calculation
refactor/PROJ-789-extract-auth-hook
chore/update-dependencies
```

## PR Conventions

- **Max 400 lines changed** (excluding generated files). Split larger work.
- **PR template** (`.github/pull_request_template.md`):

```markdown
## Summary
<!-- What changed and why -->

## Test Plan
- [ ] Unit tests pass
- [ ] E2E tests for affected flows
- [ ] Manual testing steps:

## Screenshots
<!-- If UI changes -->
```

---

## Package Scripts

```json
// package.json
{
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build",
    "analyze": "ANALYZE=true next build"
  }
}
```
