# Project Review Mode

When asked to review or audit a project, check each category and report findings.

**Detailed patterns:** `forms-auth.md` (forms/auth), `error-suspense.md` (errors/Suspense),
`data-patterns.md` (DAL/ISR/pooling), `advanced-routing.md` (parallel/intercepting routes/PPR),
`seo-scripts.md` (metadata/sitemap/scripts).

## Architecture
- Feature-based organization or anti-pattern (grouped by type)?
- `app/` thin or bloated with logic?
- Clear dependency direction (app -> features -> entities -> shared)?
- Logic/view separated in components with significant state?
- Cross-feature imports (features importing from other features)?

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

## Forms & Auth
- Forms using `useActionState` + `useFormStatus`?
- Server Actions return typed error objects (not throwing)?
- Authentication tokens in HTTP-only cookies (not localStorage)?
- Middleware protecting routes that require auth?
- Server Component layout verifying sessions for data-level auth?

## Testing & Quality
- Test files exist for components?
- Tests query by role (accessibility)?
- Storybook stories for UI components?
- TypeScript strict? Any `any`?
- Server Actions tested (validation logic as unit tests)?
- E2E tests for critical flows?

## Data & Routing
- Data Access Layer with `import 'server-only'` (not raw db calls in components)?
- `generateStaticParams` for known parameter sets?
- ISR / `cacheLife` for content that changes infrequently?
- Connection pooling configured for serverless?
- Parallel routes have `default.tsx`?
- `template.tsx` used where fresh state is needed per navigation?

## Performance
- `next/image` with `sizes` prop for responsive images?
- `next/font` used?
- Heavy components dynamically imported (`next/dynamic`)?
- Unnecessary client JS? (check bundle size)
- `generateMetadata` for SEO?
- React Compiler enabled (if applicable)?
- No deep barrel files hurting tree-shaking?
- PPR enabled for pages with mixed static/dynamic content?

## SEO
- `generateMetadata` or `metadata` export on every page?
- Open Graph / Twitter Card images set?
- JSON-LD structured data for product/article/organization pages?
- `sitemap.ts` and `robots.ts` present?
- `next/script` (not raw `<script>`) for third-party scripts?
- Canonical URLs set for duplicate content?

## Security
- No `dangerouslySetInnerHTML` without sanitization?
- Tokens in HTTP-only cookies?
- Input sanitization on both sides (Zod on server, HTML validation on client)?
- No hardcoded secrets in source?
- Environment variables: `NEXT_PUBLIC_` only for truly public values?
- `.env.local` in `.gitignore`?

## Report Format
```
## [Critical/Important/Medium] — Issue Name
**Location:** `src/components/Button.tsx:15`
**Problem:** <what's wrong>
**Impact:** <what breaks>
**Fix:** <concrete code change>
```
