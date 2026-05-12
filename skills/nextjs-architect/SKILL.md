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
For multi-file tasks: Do NOT start without a plan (Phase 0 → superpowers:writing-plans).
Do NOT write any component without first completing Phase 1 (Detection).
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
**After each phase — review your work before moving on.** Check the gate condition,
verify nothing was missed, and confirm with the user if the task is non-trivial.
Do not batch all review to the end.

### Phase 0: Planning (multi-file tasks)

For tasks involving 3+ files or 2+ components:

**REQUIRED SUB-SKILL:** Invoke `superpowers:writing-plans` to create an implementation
plan BEFORE starting Phase 1. Do NOT skip planning and jump to detection/implementation.

The plan must specify: what components to create, which folders they belong in,
dependency order, and testing approach. nextjs-architect provides the architecture
rules — writing-plans provides the execution structure.

For single-file changes or trivial edits — skip Phase 0, start at Phase 1.

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

**New project?** Follow `references/project-bootstrap.md` for step-by-step setup
(TypeScript, ESLint, Prettier, Husky, security headers, env, testing, Sentry, CI).

**tsconfig.json:** If `baseUrl` is present — remove it (deprecated, will be removed in a future TS version).
Use `paths` with relative prefixes instead: `"@/*": ["./src/*"]`. No `baseUrl` needed since TS 4.1.

**Gate:** You cannot proceed to Phase 2 without knowing: framework, styling, testing, infra.
**Review:** Confirm detection results are correct. If unsure about any signal — ask the user.

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

<Bad>
```
# WRONG — flat dump, logic in app/, no domain grouping
app/
  page.tsx              # Has 200 lines of business logic
  dashboard/page.tsx    # Fetches data, transforms, renders — all in one
components/
  Button.tsx            # Flat — no folder, no test, no variants
  Card.tsx              # Flat — stub with no states
  Input.tsx             # Flat — no error state, no label association
  UserProfile.tsx       # Should be in features, not here
  DashboardChart.tsx    # Should be in features, not here
hooks/
  useAuth.ts            # Used by one component — should be colocated
  useDashboard.ts       # Used by one page — should be next to it
```
</Bad>

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
For monorepo setup (Turborepo, shared packages), read `references/monorepo.md`.

**Gate:** You cannot proceed to Phase 3 without knowing: which model and which folder this code belongs in.
**Review:** Verify the folder structure matches the chosen model. Check dependency direction.
For non-trivial features — present the architecture decision to the user before implementing.

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
| TypeScript | `strict: true`, `noUncheckedIndexedAccess`. No `any`. `satisfies` for configs. Zod at boundaries. No `baseUrl` in tsconfig (deprecated). **Always use `import type` for interfaces, type aliases, and type-only re-exports.** Without this, esbuild/swc (used by Vite, Next.js turbopack) leave the import in JS output → runtime crash. With `verbatimModuleSyntax: true` (Vite default), tsc enforces this via TS1484. Without it, tsc is silent but runtime still breaks. |
| Performance | `next/image` with `sizes`, `next/font`, `next/dynamic`. No deep barrel files. |
| Accessibility | Semantic HTML, keyboard, visible focus, touch >= 24px, labels, contrast 4.5:1, `aria-live`. |
| UI Quality | Every interactive component MUST handle: hover, focus-visible, active, disabled, loading. No stub components. No hardcoded colors. No inline styles. No duplicates. Full catalog: `references/ui-quality.md`. |
| Design System | Tokens for color, spacing, radius, shadow, z-index, motion. One scale, one source. CVA for variants, `cn()` for merging. `prefers-reduced-motion` mandatory. Full rules: `references/design-system.md`. |
| Naming | PascalCase components, camelCase hooks/utils, `handle*` for impl, `on*` for props, `is*` booleans, no `enum` (use `as const`). Full rules: `references/naming-conventions.md`. |
| Security | CSP nonce in middleware, HSTS + X-Frame-Options in next.config, rate-limit Server Actions, `npm audit` in CI. `references/security-headers.md`. |
| Tooling | ESLint strict + a11y + import order, Prettier + Tailwind plugin, Husky + lint-staged pre-commit, conventional commits. `references/tooling.md`. |
| Code Quality | Functions ≤ 30 lines, components ≤ 150 lines, no magic numbers, no `console.log`, cleanup in `useEffect`. `references/code-quality.md`. |
| Observability | Sentry for errors, structured logging (pino), Web Vitals monitoring, feature flags. `references/observability.md`. |
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

**Gate:** You cannot proceed to Phase 4 without: component implemented, test written
(if applicable), story created (if Storybook), **AND `npx tsc --noEmit` shows
`Found 0 errors` for the changed files** (Tier 1 — see TypeScript Verification Gate).
**Review:** After EVERY file you write or modify, run `npx tsc --noEmit`. Catch errors
while context is fresh — do NOT batch type-checking to the end. Visual review
(`import type` for types, no `any`, `"use client"` boundaries, no business logic in `app/`)
happens AFTER tsc passes. If `tsc` shows errors, fix them before writing the next file.

### Phase 4: Verification

#### Step 0 — Type Safety Gate (MANDATORY — RUN BEFORE EVERYTHING ELSE)

**You cannot start the visual checklist until you have RUN these commands fresh in this turn
and quoted their output.** Visual items are easy to tick from memory; the compiler is not.

- [ ] **RUN `npx tsc --noEmit`** — output MUST end with `Found 0 errors`.
      Quote the final line verbatim. If `Found N errors in M files` — fix every error,
      re-run, repeat until 0. Not "looks fine". Not "should pass". `Found 0 errors`.
- [ ] **RUN `npx eslint <changed-paths> --max-warnings 0`** — exit code MUST be 0.
      If lint config uses a different command (`npm run lint`), use it. Warnings are errors.
- [ ] **RUN `npx vitest run <changed-paths>`** (if test files exist for affected paths) —
      output MUST show `X passed, 0 failed`. If you wrote a new test, run it.
- [ ] **RUN `npm run build`** (or `vite build`) — exit 0. **REQUIRED before commit/PR**,
      may be deferred for in-progress iterations but NEVER for completion claim.
      esbuild/swc catch errors `tsc` misses (e.g. value-typed imports under
      `verbatimModuleSyntax`).

If any command was not run in this turn, you have not completed Step 0.
Skipping Step 0 because "the change is small" / "I'm confident" / "user is in a hurry" is
the exact rationalization the TypeScript Verification Gate section below forbids.
See `references/type-safety-gate.md` for the per-tool playbook and reading-output guide.

#### Step 1 — Visual Checklist (only after Step 0 is GREEN)

- [ ] Phase 1 complete — project context detected (files read, not just user-described)
- [ ] Phase 2 complete — correct folder identified (not dumped flat, not in `app/`)
- [ ] Server Component by default — `"use client"` only with justification
- [ ] Logic/view separated if component has >1 useState or any useEffect
- [ ] Styling matches project convention (one approach, not mixed)
- [ ] Test file created and queries by `getByRole`
- [ ] Story file created (if Storybook present)
- [ ] `error.tsx` in route segments that fetch data or have async Server Components
- [ ] `<Suspense>` with skeleton fallback around async content
- [ ] Semantic HTML, keyboard accessible, labels linked
- [ ] Strict TypeScript — no `any`, all params typed (verified by Step 0, not by eye)
- [ ] All type-only imports use `import type` (verified by Step 0 under `verbatimModuleSyntax`)
- [ ] UI components have all states (hover, focus-visible, disabled, loading)
- [ ] No hardcoded colors — theme tokens only. No inline styles for static values
- [ ] No duplicated components — one canonical version in `components/ui/`
- [ ] ui/ components in subfolders (not flat) when they have states/variants
- [ ] `next/image` with `sizes`, `next/font` for fonts
- [ ] `NEXT_PUBLIC_` only for client-visible env vars
- [ ] Naming conventions followed (PascalCase components, `handle*`/`on*`, `is*` booleans)
- [ ] No `console.log` — use structured logger for server-side
- [ ] `useEffect` cleanup for subscriptions, timers, fetch (AbortController)
- [ ] Import order: React → external → @/ → relative → types
- [ ] Docker/CI updated if infrastructure exists

**If Step 0 fails or any Step 1 item fails, go back. Do not ship incomplete work.**
**Do not claim completion without Step 0 evidence quoted in this turn.**

---

## TypeScript Verification Gate

This section is the contract that makes Phase 4 Step 0 binding. It specializes
`superpowers:verification-before-completion` to the TS/React stack — that skill says
"RUN, READ, VERIFY"; this section says **which** commands and **what** their output must show.

### The Iron Law (TypeScript)

```
NO COMPLETION CLAIM WITHOUT FRESH TSC OUTPUT IN THIS TURN
```

If you have not run `tsc --noEmit` in the current message after your last code change,
you cannot claim the work compiles, is type-safe, or is ready.
Memory of a previous run does not count. "Tsc passed earlier" does not count.

### Three Tiers

| Tier | When | Commands | Why |
|------|------|----------|-----|
| **1 — Incremental** | After EVERY file written/modified | `npx tsc --noEmit` | Catches errors while you remember the change. Seconds with project references / watch. |
| **2 — Completion (Phase 4 Step 0)** | Before ANY completion claim | `npx tsc --noEmit` + `npx eslint --max-warnings 0` + `npx vitest run` (if tests exist) | Proves the whole project compiles, lints, tests. |
| **3 — Pre-commit / Pre-PR** | Before commit, push, or PR | `npm run build` (`next build` / `vite build`) | esbuild/swc differ from tsc — only build catches some classes of errors (value-typed imports under `verbatimModuleSyntax`, runtime type stripping, asset bundling). |

**Tier 1 and Tier 2 are MANDATORY. Tier 3 is MANDATORY before commit/PR but may be deferred during iteration.**

### The Gate Function

Before saying "done", "готово", "ready", "passed", "complete", "shipped", or any synonym:

1. **IDENTIFY** — which commands prove the claim?
2. **RUN** — execute fresh, in this turn, in full (no partial paths unless the project supports project references)
3. **READ** — full output, exit code, error count
4. **VERIFY** — does output confirm the claim?
   - `tsc`: must end with `Found 0 errors.`
   - `eslint`: must exit 0 (no warnings if `--max-warnings 0`)
   - `vitest`: must show `X passed, 0 failed`
   - `build`: must exit 0
5. **QUOTE** — include the relevant output line in your reply
6. **ONLY THEN** — claim completion

Skip any step → you are lying, not verifying. Even if the work is actually correct, claiming completion without evidence is the violation.

### Claim → Evidence Map

| Claim | Required evidence (this turn) | Not sufficient |
|-------|-------------------------------|----------------|
| "no `any` types" | `tsc --noEmit` → `Found 0 errors` (with `noImplicitAny`) | Visual scan; "I didn't write `any`" |
| "imports are correct" | `tsc --noEmit` (with `verbatimModuleSyntax: true`) | "I used `import type` where I remembered" |
| "props match upstream component" | `tsc --noEmit` against the consumer file | "I read the upstream file" (or worse — assumed) |
| "no unused vars" | `eslint` → exit 0 | Visual scan |
| "tests pass" | `vitest run <path>` → `X passed, 0 failed` | "I wrote tests" / "the test file exists" |
| "builds in production" | `next build` / `vite build` → exit 0 | "tsc passed" |
| "Phase 4 complete" | Tier 2 ran fresh, output quoted | Visual checklist ticked from memory |
| "Feature ready for demo" | Tier 2 + Tier 3 both passed | Anything less |

### Reading the Output Correctly

- `Found 0 errors.` (with period) → pass
- `Found N errors in M files.` → fail. Fix every one. ANY `error TS` line in output = fail, regardless of summary.
- Exit code: `tsc` returns 0 on success, non-zero on errors. Use `echo $?` (bash) or `$LASTEXITCODE` (PowerShell) when unsure.
- Build tools sometimes succeed despite warnings — treat warnings as errors in CI/PR claims.
- "0 errors" in a SUBSET of the project does not prove the WHOLE project compiles. If you ran tsc on a subpath, the global claim still requires a full-project run.

### Rationalization Prevention (TS-specific)

| Excuse | Reality |
|--------|---------|
| "`verification-before-completion` didn't say which commands" | This section does. Run them. |
| "This change is one file, tsc is overkill" | Incremental `tsc --noEmit` is seconds. Run it. |
| "I read the upstream file, I know the props" | Read ≠ verify. `tsc` proves the binding. |
| "tsc passed earlier in this session" | Today's edits need today's run. Now. |
| "esbuild will catch it at build time" | Build is Tier 3. You are at Tier 1-2. Run tsc NOW. |
| "I'm just iterating, will check at the end" | Errors compound. Run after EVERY file. |
| "User is in a hurry / demo in 10 minutes" | False "done" is slower than a 3-second tsc. |
| "The test file exists, that's enough" | Existence ≠ passing. Run `vitest run`. |
| "I fixed the obvious errors, the rest look harmless" | Fix all. Re-run. Repeat until `Found 0 errors`. |
| "tsc errors are just warnings really" | They are errors. Zero means zero. |
| "It works in dev mode" | Dev mode skips type-checking. Tier 1-3 commands are the truth. |

### Review-Mode Variant (auditing existing code)

When asked to review/audit a project, BEFORE any architectural analysis:

1. Run `npx tsc --noEmit` and capture the **full** error list.
2. Group errors by file and category.
3. Report counts at the top of your review: "Found N errors in M files: [breakdown]".
4. Architectural review follows TYPE-error triage. Don't bury TS errors under style critique.

See `references/review-checklist.md` for the full review-mode workflow.

### Red Flags — STOP

- About to say "готово" / "done" / "ready" / "passes" without having JUST run `tsc`
- Writing the next file while the previous file's `tsc` errors are unresolved
- Trusting an import because you read the upstream file
- Skipping `tsc` because "this change is tiny"
- Running `tsc`, seeing errors, fixing some, claiming done without re-running
- Stating "no `any`" without a `tsc` run to prove it
- Pasting code into the answer without running it through `tsc`

All of these mean: **STOP. Run `tsc --noEmit`. Quote its output. Then continue.**

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
- "This Button/Input only needs to render, I'll add states later"
  → A component without hover, focus-visible, disabled, loading is incomplete. Add them now.
- "I'll keep this inline, it's only used once"
  → If it exceeds 30 lines or has its own state, extract to `components/`. If the same
    pattern appears anywhere else, it MUST be a shared component.
- "I'll use a hardcoded color here, the theme doesn't have this shade"
  → Add the token to the theme. Never hardcode colors.
- "I'll copy this import block from the original file"
  → Check every imported symbol: is it a runtime value (function, class, const) or a type
    (interface, type alias)? Always use `import type { X }` or `import { type X }` for types.
    esbuild/swc (Vite, Turbopack) don't type-check — they leave value imports in JS output.
    If the symbol is type-only, the JS import fails at runtime (white screen).
    `verbatimModuleSyntax: true` makes tsc catch this (TS1484), but without it tsc is silent.

### Red Flags in Existing Code (Review Mode)

Use `references/review-checklist.md` for full audit. Key signals:
- `"use client"` on components with no interactivity
- `useState` + `useEffect` for data fetching in Next.js
- Missing `error.tsx` or `<Suspense>` boundaries
- `any` types, `dangerouslySetInnerHTML` with user input, hardcoded secrets
- UI components without states (no hover, focus-visible, disabled, loading)
- Hardcoded colors (`bg-[#...]`) instead of theme tokens
- Inline styles (`style={{}}`) for static values
- Duplicated component implementations (2+ Buttons/Inputs across project)
- Inputs without `<label>`, forms without error states, selects without keyboard support
- Inconsistent spacing, colors, or patterns across pages
- No security headers (CSP, HSTS) in production config
- `console.log` in committed code (use structured logger)
- Missing `useEffect` cleanup (timers, subscriptions, fetch without AbortController)
- Inconsistent naming (mixing camelCase/PascalCase files, handle*/on* props)
- `baseUrl` in tsconfig.json (deprecated — remove and use relative `paths`)
- Auth only in middleware — middleware is NOT a security boundary (CVE-2025-29927)
- Server Actions without auth checks — they are public HTTP endpoints, callable directly
- `typeof window !== 'undefined'` in render output — causes hydration mismatch
- `cookies()`/`headers()` inside `"use cache"` — runtime error, read outside and pass as args
- Tailwind v3 syntax in a v4 project (`bg-opacity-*`, `tailwind.config.js`)
- Type-only symbols imported without `import type` (common after refactoring/extraction;
  with `verbatimModuleSyntax` tsc catches via TS1484, without it only runtime reveals the bug)

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
| "I'll skip `tsc` for this one file" | No. `tsc --noEmit` after EVERY file. Tier 1 of Type Safety Gate. |
| "verification-before-completion is abstract — I'll do my own check" | The Type Safety Gate section specializes it. Run those exact commands. |
| "I read the imported file, the props are correct" | Read ≠ verify. Run `tsc`. It's seconds. |
| "User said urgent, no time for tsc" | A 3-second `tsc` is faster than shipping a broken type and rolling back. |

---

## Integration with Other Skills

**Required workflow skills:**
- **REQUIRED SUB-SKILL:** `superpowers:writing-plans` — Create implementation plan
  BEFORE Phase 1 for tasks with 3+ files. Do NOT skip to implementation without a plan.
- **REQUIRED SUB-SKILL:** `superpowers:verification-before-completion` — Run verification
  commands in Phase 4 before claiming work is done. Evidence before assertions.

**Recommended skills (invoke when applicable):**
- `superpowers:brainstorming` — Brainstorm design before Phase 0/Phase 2.
  Architecture decisions are easier when scope is clear.
- `superpowers:test-driven-development` — TDD requires testable components.
  Logic/view separation makes this possible.
- `superpowers:systematic-debugging` — Common Next.js bugs (hydration mismatch,
  stale cache, missing Suspense) have specific diagnostic paths.
- `superpowers:requesting-code-review` — Use the Phase 4 checklist as review criteria.

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

> **Skill architecture note:** Domain-specific Reference skills require detection logic,
> architecture rules, and version-specific guidance in the core — these cannot be deferred
> to references without breaking the phased workflow. Core: ~1,800 words. References: 20 files.
