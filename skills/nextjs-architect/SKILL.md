---
name: nextjs-architect
description: >
  Use when working with Next.js or React projects: creating components, pages, routes,
  tests, Storybook stories, or scaffolding. Also for reviewing, auditing, or refactoring
  React/Next.js architecture. Applies to React+Vite projects too.
---

# Next.js Architect

## The Iron Law

**SERVER FIRST, ALWAYS.**

Every component is a Server Component until you prove it needs client interactivity.
Every file lives in `features/`, `entities/`, or `shared/` — never business logic in `app/`.
Every component with state has a test. No `any`. No exceptions.

<HARD-GATE>
Do NOT write any component, page, or feature without first completing Phase 1 (Detection).
Do NOT ship any component without passing the Phase 4 (Verification) checklist.
Violating the letter of these rules is violating the spirit of the rules.
Thinking "just this once"? Stop. That is rationalization.
</HARD-GATE>

### When to Use

- Creating, modifying, or reviewing React components, pages, or routes
- Setting up or configuring a Next.js or React+Vite project
- Writing tests, Storybook stories, or scaffolding frontend code
- Auditing or refactoring React/Next.js architecture
- Optimizing performance, adding i18n, auth, forms, or SEO

### When NOT to Use

- Backend-only work (Node.js APIs, databases) with no React involvement
- React Native or mobile development
- Static sites without React (Hugo, Jekyll, plain HTML)
- Non-JavaScript frameworks (Django templates, Rails views, Go templates)

---

## Phased Workflow

You MUST complete each phase before proceeding to the next.

### Phase 1: Detection

Read at the start of ANY task:
- `package.json` — framework, deps, scripts
- `next.config.ts` — check for `reactCompiler`
- `tsconfig.json` — strictness, aliases
- `.storybook/main.ts` — Storybook presence

| Signal | Mode |
|--------|------|
| `next` in deps + `app/` dir | **Next.js App Router** |
| `next` in deps + `pages/` dir | **Pages Router** (legacy) |
| `vite` in deps, no `next` | **React + Vite** |
| `@storybook/*` in devDeps | **Storybook enabled** |
| `reactCompiler: true` in next.config | **React Compiler** — skip manual memoization |

**Styling:** Detect (Tailwind, CSS Modules, CSS-in-JS) and enforce consistency.
Don't impose. Don't suggest CSS-in-JS migration unless concrete SSR issues.

**Infrastructure:** If `docker-compose.yml` exists → `references/storybook-docker.md`.
If `.github/workflows/` exists → `references/cicd-pipeline.md`.

**Env vars:** `NEXT_PUBLIC_*` for client-visible only. Validate with Zod. Never commit `.env.local`.

**You cannot proceed to Phase 2 without knowing: framework, styling, testing, infra.**

### Phase 2: Architecture

Code organized by **business domain**. Inspired by Feature-Sliced Design (FSD).
**Files that change together live together.**

```
src/
  app/                    # ROUTING ONLY — thin files
    layout.tsx, page.tsx, error.tsx, loading.tsx, middleware.ts
    (marketing)/, (dashboard)/, api/webhooks/

  features/               # Business features (add-to-cart, checkout, auth)
  entities/               # Domain objects (product, user, order)
  shared/                 # Reusable infra (ui/, lib/, hooks/, types/)
```

**Rules:**
1. `app → features → entities → shared`. Never upward.
2. Features don't import other features. Compose at `app/` or extract to `entities/`.
3. `app/` is thin: only routing files. Business logic lives elsewhere.
4. `index.ts` for public API. No deep barrel re-exports.
5. Smaller projects: flat `components/` + `lib/` is fine. Migrate at ~15-20 components.

For component patterns, read `references/component-patterns.md`.
For advanced routing (parallel, intercepting, PPR), read `references/advanced-routing.md`.

**You cannot proceed to Phase 3 without knowing: which layer this code belongs in.**

### Phase 3: Implementation

**Server vs Client Boundary**

Default is Server Component. Add `"use client"` ONLY for state, effects, event handlers,
browser APIs, or client-only libraries. Push the boundary deep — extract the smallest
interactive piece.

<Good>
```tsx
// Server Component — zero JS shipped
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const product = await getProduct(id)
  return (
    <article>
      <h1>{product.name}</h1>              {/* Server */}
      <AddToCartButton productId={id} />   {/* Only this ships JS */}
    </article>
  )
}
```
</Good>

<Bad>
```tsx
// WRONG — entire page is a Client Component
'use client'
export default function Page() {
  const [product, setProduct] = useState(null)
  useEffect(() => { fetch('/api/product').then(...) }, [])  // ❌ Unnecessary client fetch
  return <div>{product?.name}</div>
}
```
</Bad>

**Quick rules:**

| Topic | Rule |
|-------|------|
| State | Server Components for server data. Context/Zustand for UI. No `useState+useEffect` for fetching in Next.js. |
| TypeScript | `strict: true`, `noUncheckedIndexedAccess`. No `any`. `satisfies` for configs. Zod at boundaries. |
| Performance | `next/image` with `sizes`, `next/font`, `next/dynamic`. No deep barrel files. |
| Accessibility | Semantic HTML, keyboard, visible focus, touch >= 24px, labels, contrast 4.5:1, `aria-live`. |
| Testing | Vitest + RTL (`getByRole`, `userEvent`). Playwright for E2E. MSW for mocking. |
| Storybook | CSF3, `satisfies Meta`, `tags: ['autodocs']`, `play` functions. |

**Reference files for deeper guidance:**
- Error handling, Suspense → `references/error-suspense.md`
- Data fetching, caching, DAL, ISR → `references/data-patterns.md`
- Forms, auth, file uploads → `references/forms-auth.md`
- SEO, metadata, sitemap → `references/seo-scripts.md`
- Theming → `references/theming.md`
- i18n → `references/i18n.md`
- Semantic variants → `references/semantic-variants.md`

**You cannot proceed to Phase 4 without: component implemented, test written, story created (if Storybook).**

### Phase 4: Verification

Before claiming work is complete, verify EVERY item:

- [ ] Phase 1 complete — project context detected
- [ ] Phase 2 complete — correct layer identified (shared/entity/feature/app)
- [ ] Server Component by default — `"use client"` only with justification
- [ ] Logic/view separated if component has >1 useState or any useEffect
- [ ] Styling matches project convention (one approach, not mixed)
- [ ] Test file created and queries by `getByRole`
- [ ] Story file created (if Storybook present)
- [ ] `error.tsx` in route segment
- [ ] `<Suspense>` with skeleton fallback around async content
- [ ] Semantic HTML, keyboard accessible, labels linked
- [ ] Strict TypeScript — no `any`, all params typed
- [ ] `next/image` with `sizes`, `next/font` for fonts
- [ ] `NEXT_PUBLIC_` only for client-visible env vars
- [ ] Docker/CI updated if infrastructure exists

**If any item fails, go back. Do not ship incomplete work.**

---

## Red Flags — STOP and Check Yourself

If you catch yourself thinking any of these, pause:

- "I'll add `use client` because I'm not sure how to do this with Server Components"
  → Use the composition pattern. Wrap only the interactive part.
- "I'll put this component in `app/` because it's faster"
  → Find the right feature. `app/` bloat is the #1 Next.js anti-pattern.
- "This component is too simple to need a separate hook"
  → If it has >1 useState or any useEffect, extract the hook.
- "I'll skip the test, it's obvious this works"
  → Tests catch regressions, not obvious bugs. Write it.
- "I'll use `any` for now and fix types later"
  → `any` spreads. Use `unknown` + type guards. Fix it now.
- "The user said keep it simple, so I'll skip the structure"
  → Simple structure IS the structure. features/entities/shared is simple.
- "The existing code doesn't follow these patterns"
  → New code follows the rules. Suggest refactoring in review mode.

### Red Flags in Existing Code (Review Mode)

Use `references/review-checklist.md` for full audit. Key signals:
- `"use client"` on components with no interactivity
- `useState` + `useEffect` for data fetching in Next.js
- Missing `error.tsx` or `<Suspense>` boundaries
- `any` types, `dangerouslySetInnerHTML` with user input, hardcoded secrets

---

## Common Rationalizations

| Excuse | Response |
|--------|----------|
| "This project is small, doesn't need features/entities" | Use features/entities. It costs nothing. Migrate pain costs weeks. Do it now. |
| "I'll refactor the architecture later" | No you won't. Architectural debt compounds. Structure it now. |
| "Hook/view separation is overkill" | Skip for <20 lines. Otherwise extract. No debate. |
| "Let's just use useState for server data" | Use Server Components. That is the point of Next.js. |
| "I'll add tests later" | Write the test now. Tests after the fact only confirm bias. |
| "`any` is fine for now" | `unknown` + type guard. Same effort, 10x safer. Do it. |
| "This is just a prototype" | Prototypes become production. Build it right or don't build it. |
| "The user said keep it simple" | Simple ≠ unstructured. These rules ARE the simple path. |
| "Server Components can't do X, I need `use client`" | Composition pattern. Push `use client` to the leaf. Read Phase 3. |

---

## Integration with Other Skills

**+ brainstorming** — Brainstorm feature design before Phase 2. Architecture decisions
are easier when scope is clear.

**+ test-driven-development** — TDD requires testable components. Logic/view separation
makes this possible.

**+ systematic-debugging** — Common Next.js bugs (hydration mismatch, stale cache,
missing Suspense) have specific diagnostic paths. Gather evidence first.

**+ requesting-code-review** — Use the Phase 4 checklist as review criteria.

---

## Quick Reference: Next.js 15 vs 16

| Next.js 15 | Next.js 16+ |
|-------------|------------|
| `middleware.ts` (Edge) | `proxy.ts` (Node.js) — RFC, verify stability |
| `fetch()` + `revalidate` option | Opt-in `"use cache"` + `cacheLife()` + `cacheTag()` |
| `experimental.ppr` | Stable PPR (expected — check release notes) |
| `next lint` | ESLint/Biome directly |
| `revalidatePath`/`revalidateTag` | `revalidateTag()` with cache profiles |
| `params` async (15+) | `await params` (same, introduced in 15) |

> Check `package.json` to determine version. When 16 APIs are marked RFC, fall back to 15.

**Convention files requiring default export:** `page.tsx`, `layout.tsx`, `error.tsx`,
`loading.tsx`, `not-found.tsx`, `default.tsx`, `template.tsx`, `global-error.tsx`.
All other components use **named exports**.

---

> **Note for skill authors:** This is a domain-specific Reference skill. Its SKILL.md
> (~1,600 words) deliberately exceeds the ~500-word target for technique/discipline skills
> because it must encode detection logic, architecture rules, and version-specific guidance
> that cannot be deferred to references without breaking the phased workflow. The tradeoff
> is justified: this skill triggers on every React task, so the core must be self-sufficient
> for the common path. Deep-dive content lives in 12 reference files (~7,000 words total).
