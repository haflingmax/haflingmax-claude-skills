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
Business logic never lives in `app/` — only routing files.
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

**Styling:** Detect and enforce consistency. Don't impose. Don't suggest CSS-in-JS
migration unless concrete SSR issues. **Detect Tailwind version:**
- v4: `@import "tailwindcss"` in CSS, `@theme` blocks, no `tailwind.config.js`
- v3: `@tailwind base/components/utilities`, `tailwind.config.js` present
- v4 syntax: opacity modifier `bg-blue-500/50` (not `bg-opacity-50`), `--color-*` prefix

**Infrastructure:** If `docker-compose.yml` exists → `references/storybook-docker.md`.
If `.github/workflows/` exists → `references/cicd-pipeline.md`.

**Env vars:** `NEXT_PUBLIC_*` for client-visible only. Validate with Zod. Never commit `.env.local`.

**tsconfig.json:** If `baseUrl` is present — remove it (deprecated in TS 6.0, removed in TS 7.0).
Use `paths` with relative prefixes instead: `"@/*": ["./src/*"]`. No `baseUrl` needed since TS 4.1.

**You cannot proceed to Phase 2 without knowing: framework, styling, testing, infra.**

### Phase 2: Architecture

**Core principle: files that change together live together** (colocation).
Detect existing structure first. If the project already has an organization — follow it.
For new projects, choose a model based on scale:

#### Model A: Vercel-Style (default for most projects)

Used by Vercel's own apps (ai-chatbot, taxonomy). Flat root, domain grouping inside
`components/` and `lib/`. No `src/` directory.

```
app/
  (auth)/                  # Route group — auth pages + layout
    actions.ts             # Server Actions colocated with route group
    login/page.tsx
    register/page.tsx
  (dashboard)/             # Route group — protected area
    _components/           # Private folder — route-specific components
    actions.ts
    overview/page.tsx
    settings/page.tsx
  api/webhooks/route.ts
  layout.tsx, globals.css

components/
  ui/                      # shadcn primitives (button, input, dialog)
  chat/                    # Domain-grouped components
    ChatPanel.tsx
    useChatPanel.ts
    ChatMessage.tsx
  billing/
    PricingTable.tsx
    usePricingTable.ts

hooks/                     # Shared hooks (useDebounce, useMediaQuery)
lib/
  db/                      # Data Access Layer (schema, queries, migrations)
  ai/                      # Domain logic
  utils.ts, constants.ts
```

#### Model B: Feature-Sliced (large-scale apps, 20+ features)

FSD-inspired layered architecture. Use when team > 5 devs or 20+ distinct features.

```
src/
  app/                     # Routing only
  features/                # Business features (add-to-cart, checkout, auth)
  entities/                # Domain objects (product, user, order)
  shared/                  # Reusable infra (ui/, lib/, hooks/)
```

**Import direction:** `app → features → entities → shared`. Never upward.
Features don't import other features. Compose at `app/` or extract to `entities/`.

#### File Organization Rules (both models)

1. **`app/` is thin.** Only routing/convention files. Business logic lives elsewhere.
2. **Every component group gets its own subfolder.** Never dump unrelated files flat
   in one directory. When a component has 2+ companion files (hook, test, sub-component),
   wrap them in a folder.
3. **Colocate by default.** Component-specific hooks live next to the component.
   Move to shared only when a second consumer appears.
4. **Group related pages.** Auth pages (Login, Register, VerifyEmail) → one folder.
   Settings tabs → one folder. Dashboard widgets → one folder.
5. **Server Actions colocate with route groups:** `app/(feature)/actions.ts`.
   Or with the feature: `components/chat/actions.ts`.
6. **Data access in `lib/db/`** — DAL functions that validate auth before returning data.
7. **No deep barrel re-exports.** `index.ts` at folder boundary only.

#### Hook Placement

| Scope | Location |
|-------|----------|
| Component-specific (1 consumer) | Next to component: `components/chat/useChatPanel.ts` |
| Feature-specific (2+ in same group) | Feature root: `components/chat/useChat.ts` |
| Shared across features (2+ unrelated consumers) | `hooks/useDebounce.ts` |

**Never put a component-specific hook in the global `hooks/` directory.**

For component file patterns, read `references/component-patterns.md`.
For advanced routing (parallel, intercepting, PPR), read `references/advanced-routing.md`.

**You cannot proceed to Phase 3 without knowing: which model and which folder this code belongs in.**

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
| TypeScript | `strict: true`, `noUncheckedIndexedAccess`. No `any`. `satisfies` for configs. Zod at boundaries. No `baseUrl` in tsconfig (deprecated TS 6.0). **With `verbatimModuleSyntax: true`: always use `import type` for interfaces, type aliases, and type-only re-exports. Never import a TypeScript type as a value — Vite/esbuild will crash at runtime even if tsc passes.** |
| Performance | `next/image` with `sizes`, `next/font`, `next/dynamic`. No deep barrel files. |
| Accessibility | Semantic HTML, keyboard, visible focus, touch >= 24px, labels, contrast 4.5:1, `aria-live`. |
| Testing | Vitest + RTL (`getByRole`, `userEvent`). Playwright for E2E. MSW for mocking. |
| Storybook | CSF3, `satisfies Meta`, `tags: ['autodocs']`, `play` functions. |

**Security (critical):**
- **Middleware is NOT a security boundary.** It can be bypassed (CVE-2025-29927).
  Enforce auth in DAL, Server Actions, and Route Handlers independently.
- **Server Actions are public HTTP endpoints.** Every exported action is callable via
  direct POST. Always validate auth inside every Server Action, not just input shape.

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
- [ ] Phase 2 complete — correct folder identified (not dumped flat, not in `app/`)
- [ ] Server Component by default — `"use client"` only with justification
- [ ] Logic/view separated if component has >1 useState or any useEffect
- [ ] Styling matches project convention (one approach, not mixed)
- [ ] Test file created and queries by `getByRole`
- [ ] Story file created (if Storybook present)
- [ ] `error.tsx` in route segment
- [ ] `<Suspense>` with skeleton fallback around async content
- [ ] Semantic HTML, keyboard accessible, labels linked
- [ ] Strict TypeScript — no `any`, all params typed
- [ ] All type-only imports use `import type` (especially after extracting hooks or moving files)
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
  → `app/` is for routing only. Put it in `components/{domain}/` or `features/`.
- "I'll put all files flat in one folder, it's simpler"
  → Group by domain. Each component group gets its own subfolder when it has 2+ files.
- "This component is too simple to need a separate hook"
  → If it has >1 useState or any useEffect, extract the hook.
- "I'll skip the test, it's obvious this works"
  → Tests catch regressions, not obvious bugs. Write it.
- "I'll use `any` for now and fix types later"
  → `any` spreads. Use `unknown` + type guards. Fix it now.
- "The user said keep it simple, so I'll skip the structure"
  → Simple structure IS the structure. `components/{domain}/` is simple.
- "The existing code doesn't follow these patterns"
  → New code follows the rules. Suggest refactoring in review mode.
- "I'll copy this import block from the original file"
  → Check every imported symbol: is it a runtime value (function, class, const) or a type
    (interface, type alias)? With `verbatimModuleSyntax`, type-only imports MUST use
    `import type { X }` or `import { type X }`. Vite strips type-only imports at build time;
    if you import a type as a value, the bundle tries to find a JS export that doesn't exist
    → white screen in browser, no error from tsc.

### Red Flags in Existing Code (Review Mode)

Use `references/review-checklist.md` for full audit. Key signals:
- `"use client"` on components with no interactivity
- `useState` + `useEffect` for data fetching in Next.js
- Missing `error.tsx` or `<Suspense>` boundaries
- `any` types, `dangerouslySetInnerHTML` with user input, hardcoded secrets
- `baseUrl` in tsconfig.json (deprecated TS 6.0 — remove and use relative `paths`)
- Auth only in middleware — middleware is NOT a security boundary (CVE-2025-29927)
- Server Actions without auth checks — they are public HTTP endpoints, callable directly
- `typeof window !== 'undefined'` in render output — causes hydration mismatch
- `cookies()`/`headers()` inside `"use cache"` — runtime error, read outside and pass as args
- Tailwind v3 syntax in a v4 project (`bg-opacity-*`, `tailwind.config.js`)
- Type-only symbols imported without `import type` when `verbatimModuleSyntax` is enabled
  (grep for interfaces/types from external packages imported as values — common after
  refactoring/extraction)

---

## Common Rationalizations

| Excuse | Response |
|--------|----------|
| "This project is small, doesn't need structure" | Use `components/{domain}/` at minimum. Group files from day one. Costs nothing. |
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
