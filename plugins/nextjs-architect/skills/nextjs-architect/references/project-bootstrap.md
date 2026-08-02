# New Project Bootstrap Checklist

Step-by-step sequence for scaffolding a production-ready Next.js project from zero.
Follow in order — each step builds on the previous.

---

## Step 1: Create Project

```bash
npx create-next-app@latest my-app --typescript --tailwind --app --src-dir --turbopack
cd my-app
```

Flags: `--typescript` (mandatory), `--tailwind` (if project uses Tailwind),
`--app` (App Router), `--src-dir` (optional — Vercel apps skip this).

---

## Step 2: TypeScript Configuration

Edit `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

- Remove `baseUrl` if present (deprecated)
- Add `noUncheckedIndexedAccess: true`
- Verify `strict: true` is set

---

## Step 3: ESLint + Prettier + Husky

```bash
# ESLint plugins
npm install -D eslint-plugin-react-hooks eslint-plugin-jsx-a11y eslint-plugin-import

# Prettier + Tailwind plugin
npm install -D prettier prettier-plugin-tailwindcss

# Husky + lint-staged + commitlint
npm install -D husky lint-staged @commitlint/cli @commitlint/config-conventional
npx husky init
```

Create files:
- `eslint.config.mjs` — see `references/tooling.md` for full config
- `.prettierrc` — `{ "printWidth": 100, "singleQuote": true, "trailingComma": "all", "semi": false, "plugins": ["prettier-plugin-tailwindcss"] }`
- `.husky/pre-commit` — `npx lint-staged`
- `.husky/commit-msg` — `npx --no -- commitlint --edit $1`
- `commitlint.config.js` — `export default { extends: ['@commitlint/config-conventional'] }`
- `package.json` `lint-staged` section — see `references/tooling.md`
- `.vscode/settings.json` + `.vscode/extensions.json` — see `references/tooling.md`

---

## Step 4: Security Headers

Edit `next.config.ts` — add security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security`
- `Referrer-Policy`
- `Permissions-Policy`

Add CSP middleware if the app has user-generated content.
See `references/security-headers.md` for full config.

---

## Step 5: Environment Validation

Create `env.ts` with Zod schema or `@t3-oss/env-nextjs`:

```bash
npm install @t3-oss/env-nextjs zod
```

Create `.env.local` (gitignored) and `.env.example` (committed with placeholders).
See `references/code-quality.md` for full pattern.

---

## Step 6: Directory Structure

Create the project skeleton:

```bash
# Vercel-style (default)
mkdir -p components/ui hooks lib/db

# Or FSD-style (large projects)
mkdir -p src/features src/entities src/shared/ui src/shared/lib src/shared/hooks
```

Set up:
- `lib/utils.ts` — `cn()` function (clsx + tailwind-merge)
- `lib/db/` — database client + DAL (if using database)
- `lib/logger.ts` — pino logger (see `references/observability.md`)
- `components/ui/` — will hold shadcn primitives

See `references/component-patterns.md` for file structure and `SKILL.md` Phase 2 for model choice.

---

## Step 7: Design System Foundation

Set up theme tokens in `app/globals.css`:
- Color tokens (semantic: `--primary`, `--destructive`, etc.)
- If dark mode needed: install `next-themes`, add ThemeProvider

Install base UI components:
```bash
npx shadcn@latest init
npx shadcn@latest add button input label
```

See `references/design-system.md` for complete token system and `references/theming.md` for dark mode.

---

## Step 8: Testing Setup

```bash
# Vitest + React Testing Library
npm install -D vitest @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom

# Playwright (E2E)
npm install -D @playwright/test
npx playwright install

# MSW (API mocking)
npm install -D msw
```

Create `vitest.config.ts` and first test to verify setup works.
See `references/component-patterns.md` testing section.

---

## Step 9: Error Handling

Create error boundaries:
- `app/error.tsx` — global error boundary
- `app/global-error.tsx` — root layout error
- `app/not-found.tsx` — 404 page
- `app/loading.tsx` — global loading skeleton

See `references/error-suspense.md` for patterns.

---

## Step 10: Observability (production)

```bash
npx @sentry/wizard@latest -i nextjs
```

Set up:
- Sentry error tracking
- Web Vitals reporting
- Health check endpoint (`app/api/health/route.ts`)

See `references/observability.md` for full setup.

---

## Step 11: CI/CD Pipeline

Create `.github/workflows/ci.yml`:
- lint, typecheck, test, build, storybook, e2e (parallel where possible)
- `npm audit` for security

See `references/cicd-pipeline.md` for full pipeline.

---

## Step 12: Documentation

- `README.md` — project overview, setup instructions, scripts
- `.github/pull_request_template.md` — PR template
- `CLAUDE.md` — instructions for AI agents working on this codebase

---

## Verification

After completing all steps, verify:

```bash
npm run lint          # No errors
npm run typecheck     # No errors  
npm run test          # Tests pass
npm run build         # Build succeeds
npm run dev           # Dev server starts
```

The project is now ready for feature development using the phased workflow (SKILL.md).
