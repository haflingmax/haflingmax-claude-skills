# TypeScript Verification Gate — Playbook

This is the deep reference for the Type Safety Gate section in `SKILL.md`. It explains
WHICH commands to run in WHICH situations, HOW to read their output, and HOW to handle
the most common error patterns. Load this file when:

- You hit a non-trivial set of TS errors and need triage guidance.
- You are doing review-mode auditing of an existing project.
- You are unsure whether a specific run satisfies the Gate.
- A user/CI tool wraps the standard commands and you need to map them.

The Iron Law is in `SKILL.md`. This file is the operations manual.

---

## 1. Command Reference by Stack

### Next.js (App Router or Pages Router)

| Tier | Command | Notes |
|------|---------|-------|
| 1 | `npx tsc --noEmit` | If project has `tsconfig.json` with `incremental: true`, second run is ~100ms. |
| 1 | `npx tsc --noEmit --watch` | Long-running. Use when iterating on many files. Quote final batch. |
| 2 | `npm run typecheck` | If defined in `package.json`. Usually wraps the above. |
| 2 | `npx eslint . --max-warnings 0` | Or `npm run lint`. Next.js projects often have `next lint` (deprecated in 16). |
| 2 | `npx vitest run` | Or `npm test`. For Jest: `npx jest`. |
| 3 | `npm run build` | Wraps `next build`. Runs full type-check + bundling. |

### React + Vite

| Tier | Command | Notes |
|------|---------|-------|
| 1 | `npx tsc --noEmit -p tsconfig.app.json` | Vite splits configs: `tsconfig.app.json` (src) and `tsconfig.node.json` (config files). Run both. |
| 1 | `npx tsc --noEmit -p tsconfig.node.json` | For vite.config.ts, plugins, scripts. |
| 2 | `npm run typecheck` | If defined. Vite projects often combine both tsconfigs here. |
| 2 | `npx eslint . --max-warnings 0` | Vite + React templates ship with ESLint. |
| 2 | `npx vitest run` | Vitest is the default test runner for Vite projects. |
| 3 | `npm run build` | Wraps `tsc -b && vite build`. Will refuse to build with TS errors. |

### Monorepo (Turborepo / Nx)

| Tier | Command | Notes |
|------|---------|-------|
| 1 | `npx tsc --build` (project references) | If `composite: true` in tsconfig. Fastest path for monorepos. |
| 2 | `npx turbo run typecheck` | Runs `typecheck` script in every package. |
| 2 | `npx turbo run lint` | Same for lint. |
| 3 | `npx turbo run build` | Full build across packages. |

---

## 2. Reading Output: The Truth Table

### tsc output

| Output ends with... | State | Action |
|---------------------|-------|--------|
| `Found 0 errors.` | PASS | Continue. |
| `Found N errors in M files.` | FAIL | Triage by section 3 below. Fix all. Re-run. |
| (no summary, just errors and exits) | FAIL | Same as above. The lack of summary = old tsc version or interrupted run. |
| (no output at all, exit 0) | PASS (silent mode) | Acceptable but quote `echo $? = 0` in your reply. |
| (errors printed, exit 0) | BUG IN YOUR SETUP | tsc with `--noEmit` should exit non-zero on errors. If it doesn't, your wrapper script is swallowing the code. Fix wrapper first. |

### eslint output

| Output | State | Action |
|--------|-------|--------|
| (empty, exit 0) | PASS | Continue. |
| `X problems (Y errors, Z warnings)` with `--max-warnings 0` and Z > 0 | FAIL | Fix all warnings — they are errors at this gate. |
| `Cannot read config "..."` | BLOCKED | Fix lint config before claiming verification. |

### vitest output

| Output | State | Action |
|--------|-------|--------|
| `Test Files X passed (X)` + `Tests Y passed (Y)` | PASS | Continue. |
| `Tests Y failed (Y)` | FAIL | Triage individual tests. |
| `No test files found` for the paths you ran | UNDETERMINED | Either (a) you have no tests for the change — write one, OR (b) you ran the wrong path. Verify scope. |

### Build (next/vite)

| Output | State | Action |
|--------|-------|--------|
| (success summary, exit 0) | PASS | Continue. |
| `Failed to compile` / `Build failed` | FAIL | Read error class — TS, ESLint, missing module, runtime check. |
| `Error occurred prerendering page` | FAIL | Server Component runtime error during static generation. Don't ship. |

---

## 3. Common TS Error Patterns and Fixes

### TS2322 / TS2353 — Object literal / unknown prop

```
Type '{ src: string; }' is not assignable to type 'UserAvatarProps'.
  Object literal may only specify known properties, and 'src' does not exist in type 'UserAvatarProps'.
```

**Cause:** You passed a prop that the target component doesn't accept.
**Fix:** Read the component's actual prop signature (`Read` the file). Use the correct prop name.
**Prevention:** Read upstream component BEFORE writing the consumer.

### TS2741 — Missing required prop

```
Property 'alt' is missing in type '{ src: string; }' but required in type 'ImageProps'.
```

**Cause:** Forgot a required prop.
**Fix:** Provide it. If the value is unknown to you, ask the user — don't make it optional in the upstream type.

### TS2613 / TS2614 — Default vs named export mismatch

```
Module '"./UserAvatar"' has no exported member 'UserAvatar'. Did you mean to use 'import UserAvatar from "./UserAvatar"' instead?
```

**Cause:** You used `import { X }` for a default export, or vice versa.
**Fix:** Match the export style. Convention in this skill: components use named exports EXCEPT Next.js routing files (`page.tsx`, `layout.tsx`, etc.).

### TS1484 — Type used as value with `verbatimModuleSyntax`

```
'UserAvatarProps' is a type and must be imported using a type-only import when 'verbatimModuleSyntax' is enabled.
```

**Cause:** You imported a type as a value. esbuild/swc leave it in JS output → runtime crash.
**Fix:** `import type { UserAvatarProps } from "./UserAvatar"`. Or `import { type UserAvatarProps, UserAvatar } from "./UserAvatar"` if you need both.

### TS2532 / TS2533 — Possibly undefined / null

```
Object is possibly 'undefined'.
```

**Cause:** Strict null checks. Array access, `Map.get`, optional chains.
**Fix:** Narrow with `if`, `?.`, `??`, or non-null assertion `!` (last resort, with comment explaining invariant).
**Note:** With `noUncheckedIndexedAccess`, every array index is `T | undefined`. Use `arr.at(0) ?? fallback` or check `arr.length`.

### TS18046 — `unknown` type

```
'err' is of type 'unknown'.
```

**Cause:** Catch clauses and JSON.parse return `unknown` under `useUnknownInCatchVariables`.
**Fix:** Type guard: `if (err instanceof Error) { ... }` or Zod schema parse.

### TS7016 — Missing type declarations

```
Could not find a declaration file for module 'foo'.
```

**Cause:** Library has no bundled types and `@types/foo` is not installed.
**Fix:** `npm i -D @types/foo`. If no @types exist — write `foo.d.ts` with `declare module 'foo';` (last resort, with TODO).

### TS6133 — Unused variable (with `noUnusedLocals` or ESLint)

**Fix:** Delete the variable. Don't prefix with `_` unless it's a destructuring placeholder; prefer deletion.

---

## 4. Review-Mode Workflow (auditing existing code)

When the task is "review this project" / "audit" / "find issues":

**Step 1 — Type-error census (BEFORE any architectural reading):**

```bash
npx tsc --noEmit 2>&1 | tee tsc-report.txt
wc -l tsc-report.txt   # number of error lines (approximate count)
grep -c "error TS" tsc-report.txt
```

Report at the top of your audit:

```
## Type Safety Status
Errors: N across M files
Top error codes: TS2322 (X), TS1484 (Y), TS2741 (Z)
File hotspots: src/components/Foo.tsx (12), src/hooks/useBar.ts (8), ...
```

If N > 0, **TS errors are the #1 finding regardless of architecture issues**. Architectural critique on top of a broken type graph is gardening a burning building.

**Step 2 — Lint census:**

```bash
npx eslint . --max-warnings 0 --format json > eslint-report.json
```

**Step 3 — Test census:**

```bash
npx vitest run --reporter=verbose 2>&1 | tail -50
```

Report failure count + flakiness signals.

**Step 4 — Architectural / convention review** — follow `references/review-checklist.md`.

**Step 5 — Prioritized fix plan** with TS errors at the top, then security, then architecture, then style.

---

## 5. Edge Cases

### "The project has thousands of pre-existing errors, what do I do?"

- For NEW code you write: `tsc --noEmit` must NOT add any new errors. Compare error count before/after.
- For review/audit: report the baseline, recommend a TS-error reduction plan.
- Do NOT ignore — flag explicitly.

### "tsc is slow on this project"

- Enable `incremental: true` in tsconfig. Second run becomes ~100ms.
- Use project references (`composite: true`, `references: []`) for monorepos.
- Run `tsc --build --watch` in background during development.

### "I changed only a markdown / config file"

- Tier 1 (incremental tsc) is unnecessary for non-TS files.
- But if you also touched any `.ts` / `.tsx` — Tier 1 applies.
- Tier 2 (Phase 4 Step 0) ALWAYS applies before completion claim, even for "just config" changes — config changes (`tsconfig.json`, `next.config.ts`) can break the whole project.

### "User explicitly says 'skip the type check'"

- Confirm: "Skipping the type-safety gate means I cannot claim the code is type-safe. Acceptable?"
- If user confirms — proceed, but in your final reply state: "Type-safety gate was skipped at user request. The code has NOT been type-checked. Risk: [list potential error classes]."

### "ESLint config is missing or fails to load"

If `eslint` exits with `No ESLint configuration found` or similar:

1. Check `package.json` for a `lint` script — try `npm run lint` instead.
2. If no lint config exists at all in the project — note it in your final reply
   ("ESLint not configured in this project; Tier 2 lint check was not enforceable"),
   and continue with `tsc` and `vitest` as the binding parts of Step 0.
3. Do NOT silently skip — surface the gap. Suggest adding ESLint in your final reply
   (with a pointer to `references/tooling.md` if it exists).
4. Same logic for missing `vitest` config: if no tests exist anywhere, state that fact
   explicitly and continue. Do NOT pretend tests "passed".

---

## 6. Automation Hooks (for projects that have them)

If the project has `.husky/pre-commit` or a `lint-staged` config:

- These run on commit, not before. The Gate must run BEFORE the completion claim, not at commit.
- Pre-commit hooks are belt-and-suspenders, not a substitute for the Gate.
- If a pre-commit hook fails, that is evidence the Gate would have caught it earlier — do not bypass the hook to "fix later".

If the project has GitHub Actions / CI:

- CI runs after push. Same logic: Gate runs BEFORE you push.
- "CI will catch it" is a Tier 3 deferral, not a Tier 1-2 excuse.

---

## 7. Frequently Used Snippets

```bash
# Tier 1 — fastest incremental TS check after a single file edit
npx tsc --noEmit

# Tier 2 — full Phase 4 Step 0 verification
npx tsc --noEmit && npx eslint . --max-warnings 0 && npx vitest run

# Tier 3 — production build (slow, run before commit/PR)
npm run build

# Tier-1-watch — keep tsc running in background while you iterate
npx tsc --noEmit --watch --preserveWatchOutput

# Review-mode census
npx tsc --noEmit 2>&1 | grep -c "error TS" || echo "0"
```

```powershell
# PowerShell equivalents (Windows)
npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { Write-Host "TSC FAILED" }
npx eslint . --max-warnings 0; if ($LASTEXITCODE -ne 0) { Write-Host "ESLINT FAILED" }
```
