# Monorepo Patterns

Guide for Next.js projects in monorepo setups (Turborepo, Nx, pnpm workspaces).

---

## When to Use a Monorepo

- 2+ apps sharing UI components or business logic
- Design system used across multiple products
- Backend + frontend in same repo (full-stack)
- Shared TypeScript types between services

Not needed: single Next.js app, even if large.

---

## Recommended Structure (Turborepo + pnpm)

```
monorepo/
├── apps/
│   ├── web/                    # Next.js main app
│   │   ├── app/
│   │   ├── next.config.ts
│   │   ├── package.json        # "name": "@acme/web"
│   │   └── tsconfig.json       # extends ../../tsconfig.base.json
│   ├── admin/                  # Next.js admin panel
│   │   ├── app/
│   │   ├── next.config.ts
│   │   └── package.json        # "name": "@acme/admin"
│   └── docs/                   # Documentation site
│
├── packages/
│   ├── ui/                     # Shared design system
│   │   ├── src/
│   │   │   ├── button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── index.ts
│   │   │   ├── input/
│   │   │   └── index.ts        # Public API: export { Button } from './button'
│   │   ├── package.json        # "name": "@acme/ui", "exports": { ".": "./src/index.ts" }
│   │   └── tsconfig.json
│   ├── lib/                    # Shared utilities
│   │   ├── src/
│   │   │   ├── cn.ts
│   │   │   ├── format.ts
│   │   │   └── validators.ts
│   │   └── package.json        # "name": "@acme/lib"
│   ├── types/                  # Shared TypeScript types
│   │   ├── src/
│   │   │   └── index.ts
│   │   └── package.json        # "name": "@acme/types"
│   └── tsconfig/               # Shared TS configs
│       ├── base.json
│       ├── nextjs.json
│       └── react-library.json
│
├── turbo.json                  # Turborepo pipeline
├── pnpm-workspace.yaml         # Workspace definition
├── package.json                # Root: devDeps only (turbo, typescript, eslint)
└── tsconfig.base.json          # Root tsconfig
```

---

## Key Configuration Files

### pnpm-workspace.yaml

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "typecheck": {
      "dependsOn": ["^build"]
    }
  }
}
```

### Shared tsconfig (packages/tsconfig/base.json)

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "bundler",
    "module": "esnext",
    "target": "es2022",
    "jsx": "react-jsx",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "isolatedModules": true
  }
}
```

### Next.js tsconfig (packages/tsconfig/nextjs.json)

```json
{
  "extends": "./base.json",
  "compilerOptions": {
    "plugins": [{ "name": "next" }],
    "noEmit": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### App tsconfig (apps/web/tsconfig.json)

```json
{
  "extends": "@acme/tsconfig/nextjs.json",
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## Shared UI Package

### package.json (packages/ui)

```json
{
  "name": "@acme/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    ".": "./src/index.ts",
    "./button": "./src/button/index.ts",
    "./input": "./src/input/index.ts"
  },
  "peerDependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@acme/tsconfig": "workspace:*",
    "typescript": "^5.7.0"
  }
}
```

### Consuming in apps

```tsx
// apps/web/app/page.tsx
import { Button } from '@acme/ui/button'
import { cn } from '@acme/lib'
```

### next.config.ts (transpile workspace packages)

```ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  transpilePackages: ['@acme/ui', '@acme/lib'],
}

export default config
```

**Critical:** `transpilePackages` is required for workspace packages — Next.js does not
transpile `node_modules` by default. Without this, you get "Module parse failed" errors.

---

## Rules

1. **Shared UI in `packages/ui/`**, not duplicated per app. Apps import from `@acme/ui`.
2. **One source of truth for tsconfig.** Shared configs in `packages/tsconfig/`, apps extend.
3. **`exports` field in package.json** for each package — explicit public API.
   Use subpath exports (`@acme/ui/button`) for tree-shaking.
4. **`transpilePackages`** in every app's `next.config.ts` for workspace dependencies.
5. **Internal packages are `"private": true`** — never published to npm.
6. **`dependsOn: ["^build"]`** in turbo.json ensures packages build before apps.
7. **Consistent tooling:** same ESLint config, same Prettier config, same TS strictness
   across all packages and apps.
8. **Don't share `node_modules`** between apps — each app resolves its own deps.
   pnpm handles this correctly with its content-addressed store.

---

## Common Pitfalls

- **Forgetting `transpilePackages`:** Pages crash with "Module parse failed" or JSX syntax errors.
- **Circular dependencies between packages:** `ui` imports from `lib`, `lib` imports from `ui`.
  Enforce unidirectional: `apps → ui → lib → types`. Never upward.
- **Different React versions across apps:** All apps MUST use the same React version.
  Pin in root `package.json` with `pnpm.overrides`.
- **Tailwind in shared packages:** Each app runs its own Tailwind build. Shared `@acme/ui`
  components use Tailwind classes but the Tailwind config is in each app, not the package.
  Add `'../../packages/ui/src/**/*.tsx'` to each app's Tailwind content paths.
- **Server Components in shared packages:** Mark the package as supporting RSC by NOT
  adding `"use client"` at the package level — add it per-component where needed.

---

## Nx Alternative

If using Nx instead of Turborepo:
- `nx.json` replaces `turbo.json`
- `project.json` per package replaces inferred tasks
- `@nx/next` plugin for Next.js integration
- Same workspace structure (apps/ + packages/)
- Same rules apply for tsconfig sharing and transpilePackages
