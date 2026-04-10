# Project Review Mode

When asked to review or audit a project, check EVERY category below and report findings.

**Detailed patterns:** `forms-auth.md`, `error-suspense.md`, `data-patterns.md`,
`advanced-routing.md`, `seo-scripts.md`, `ui-quality.md`, `design-system.md`,
`naming-conventions.md`, `security-headers.md`, `tooling.md`, `code-quality.md`,
`observability.md`.

---

## Architecture
- Feature-based organization or anti-pattern (grouped by type)?
- `app/` thin or bloated with logic?
- Clear dependency direction?
- Logic/view separated in components with significant state?
- Cross-feature imports (features importing from other features)?
- Every component group in its own subfolder (not flat)?
- Page-specific hooks colocated (not in global `hooks/`)?
- Related pages grouped (`auth/`, `settings/`)?

## Server/Client
- Is `"use client"` overused? (Most common Next.js anti-pattern)
- Components marked `"use client"` with no event handlers, state, or browser APIs?
- Are Server Components doing client work?
- Is data fetched on server or via `useState+useEffect`?

## Error Handling & Suspense
- `error.tsx` present in route segments that fetch data?
- `global-error.tsx` at root?
- `<Suspense>` boundaries around async Server Components?
- Meaningful skeleton fallbacks (not just spinners)?
- `not-found.tsx` for routes that look up resources by ID?

## Data & State
- `"use cache"` with explicit `cacheLife()` (Next.js 16)?
- `fetch()` caching strategy appropriate (Next.js 15)?
- Server Actions validating server-side with Zod?
- Client state only for UI, not server data?
- No `useState+useEffect` for data fetching in Next.js context?
- Data Access Layer with `import 'server-only'`?
- `generateStaticParams` for known parameter sets?
- Connection pooling configured for serverless?

## Forms & Auth
- Forms using `useActionState` + `useFormStatus`?
- Server Actions return typed error objects (not throwing)?
- Server Actions validate auth inside (they are public endpoints)?
- Authentication tokens in HTTP-only cookies (not localStorage)?
- Middleware for UX redirects only (NOT security boundary)?

## UI Component Quality (references/ui-quality.md)
- Components have ALL interactive states (hover, focus-visible, active, disabled, loading)?
- Button: variants, sizes, loading state, `aria-disabled`?
- Input: associated `<label>`, `aria-invalid`, `aria-describedby` for errors?
- Input types: correct `inputMode`, `autoComplete` per type (email, password, tel)?
- Select/Dropdown: keyboard navigation (arrows, Escape, type-ahead)?
- Dialog/Modal: focus trap, Escape to close, focus returns to trigger?
- No stub components (render-only without states)?
- UI components in subfolders (not flat files in `ui/`)?

## Design System Consistency (references/design-system.md)
- All colors reference theme tokens (no hardcoded hex `bg-[#...]`)?
- No inline styles (`style={{}}`) for static values?
- Spacing from scale only (no arbitrary `p-[13px]`)?
- Consistent spacing project-wide (same form gap, same section gap)?
- Border radius from discrete scale (not arbitrary)?
- Z-index from named scale (not raw numbers)?
- `prefers-reduced-motion` respected for animations?
- One canonical version of each component (no duplicates)?
- CVA for component variants (not ad-hoc ternaries)?
- `cn()` for class merging (not string concatenation)?
- Consistent empty states, loading states, error patterns across pages?
- Consistent form patterns (labels, error display, required indicators)?

## Naming Conventions (references/naming-conventions.md)
- Files: PascalCase components, camelCase hooks/utils, kebab-case routes?
- Event handlers: `handle*` for implementations, `on*` for props?
- Boolean props/state: `is*`, `has*`, `should*`, `can*` prefix?
- Types: `interface` for shapes, `type` for unions. `*Props` suffix. No `I` prefix?
- Constants: `UPPER_SNAKE_CASE` for compile-time, camelCase for runtime?
- `as const` objects preferred over `enum`?
- Server Actions: verb-noun + `Action` suffix?
- No generic names (`data`, `info`, `item`) — be specific?

## Security (references/security-headers.md)
- Security headers in `next.config.ts` (HSTS, X-Frame-Options, X-Content-Type-Options)?
- Content Security Policy (CSP) with nonces?
- Rate limiting on public Server Actions and Route Handlers?
- No `dangerouslySetInnerHTML` with user content?
- Dependency security: `npm audit` in CI, Dependabot/Renovate enabled?
- CSRF: Server Actions auto-validate Origin. Route Handlers need explicit check?
- Session cookies: `HttpOnly`, `Secure`, `SameSite=Lax`?
- No hardcoded secrets in source. `.env.local` in `.gitignore`?
- `NEXT_PUBLIC_` only for truly public values?

## Tooling & Conventions (references/tooling.md)
- ESLint configured: `@typescript-eslint/strict`, `react-hooks`, `jsx-a11y`, `import`?
- `consistent-type-imports` ESLint rule (enforces `import type`)?
- Import ordering enforced (React → external → @/ → relative → types)?
- Prettier configured with `prettier-plugin-tailwindcss`?
- Pre-commit hooks (Husky + lint-staged)?
- Conventional commits enforced (commitlint)?
- `.vscode/settings.json` + `.vscode/extensions.json` committed?
- PR template (`.github/pull_request_template.md`)?

## Code Quality (references/code-quality.md)
- Functions ≤ 30 lines, components ≤ 150 lines?
- Cyclomatic complexity ≤ 15?
- No magic numbers (extracted to named constants)?
- No `console.log` in committed code (use structured logger)?
- `useEffect` cleanup for all subscriptions, timers, fetch (AbortController)?
- React 19 ref cleanup used where applicable?
- Dead code removed (no unused exports, `ts-prune`)?
- TODOs reference ticket numbers?
- Shared component props documented with TSDoc?
- Environment variables validated at build time (Zod / `@t3-oss/env-nextjs`)?
- Virtual scrolling for lists > 100 items?

## Observability (references/observability.md)
- Error tracking configured (Sentry or equivalent)?
- `error.tsx` captures exceptions to Sentry?
- Web Vitals monitored (LCP, CLS, INP)?
- Structured logging (pino or equivalent) — no `console.log` in production?
- Health check endpoint (`/api/health`)?
- Feature flags for gradual rollouts?

## Testing
- Test files exist for components?
- Tests query by `getByRole` (accessibility)?
- Storybook stories for UI components?
- `userEvent` (not `fireEvent`)?
- Server Actions: validation tested as unit tests?
- E2E tests for critical flows?
- MSW for API mocking?

## Performance
- `next/image` with `sizes` prop?
- `next/font` used?
- Heavy components dynamically imported (`next/dynamic`)?
- Bundle size tracked (`@next/bundle-analyzer`)?
- Web Vitals within budgets (LCP < 2.5s, CLS < 0.1, INP < 200ms)?
- React Compiler enabled (if applicable)?
- No deep barrel files hurting tree-shaking?
- Virtual scrolling for large lists?
- `next/script` for third-party scripts (not raw `<script>`)?

## SEO
- `generateMetadata` or `metadata` export on every page?
- Open Graph / Twitter Card images?
- JSON-LD structured data for product/article pages?
- `sitemap.ts` and `robots.ts` present?
- Canonical URLs for duplicate content?

## TypeScript
- `strict: true`, `noUncheckedIndexedAccess: true`?
- No `any` types?
- No `baseUrl` in tsconfig (deprecated)?
- All type-only imports use `import type`?
- `verbatimModuleSyntax` enabled (Vite projects)?

---

## Report Format

```
## [Critical/Important/Medium] — Issue Name
**Location:** `src/components/Button.tsx:15`
**Problem:** <what's wrong>
**Impact:** <what breaks>
**Fix:** <concrete code change>
```

Prioritize: Security > Correctness > Performance > Quality > Style.
