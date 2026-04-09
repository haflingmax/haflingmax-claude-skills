# Code Quality Standards

Metrics, documentation, memory leak prevention, and dead code management.

---

## Code Complexity Limits

| Metric | Limit | Enforcement |
|--------|-------|-------------|
| Component length | ≤ 150 lines | Extract sub-components or hooks |
| Function length | ≤ 30 lines | Extract helper functions |
| Cyclomatic complexity | ≤ 15 | ESLint `complexity` rule |
| Function parameters | ≤ 4 | Use options object pattern |
| Nesting depth | ≤ 3 levels | Early returns, extract functions |

### Early Return Pattern

```tsx
// GOOD — flat, readable
export function getDiscount(user: User, product: Product): number {
  if (!user.isPremium) return 0
  if (!product.isDiscountable) return 0
  if (product.price < 10) return 0

  return product.price * 0.1
}

// BAD — deeply nested
export function getDiscount(user: User, product: Product): number {
  if (user.isPremium) {
    if (product.isDiscountable) {
      if (product.price >= 10) {
        return product.price * 0.1
      }
    }
  }
  return 0
}
```

---

## Magic Numbers and String Literals

Extract to named constants. ESLint `no-magic-numbers` (exceptions: 0, 1, -1, HTTP codes).

```tsx
// BAD
if (items.length > 10) { ... }
await new Promise(r => setTimeout(r, 300))
if (response.status === 429) { ... }

// GOOD
const MAX_VISIBLE_ITEMS = 10
const DEBOUNCE_MS = 300
const HTTP_TOO_MANY_REQUESTS = 429

if (items.length > MAX_VISIBLE_ITEMS) { ... }
await new Promise(r => setTimeout(r, DEBOUNCE_MS))
if (response.status === HTTP_TOO_MANY_REQUESTS) { ... }
```

---

## Console.log Policy

- **ESLint rule:** `'no-console': ['warn', { allow: ['warn', 'error'] }]`
- Development: `console.log` OK for quick debugging — lint will warn.
- Production: ZERO `console.log`. Use structured logger (`pino`) for server.
- CI: `no-console` as `error` — block PRs with committed console.log.
- **Never log:** passwords, tokens, session IDs, PII, full request bodies.

---

## TODO / FIXME Tracking

- ESLint `no-warning-comments` as `warn` — flag but don't block.
- Every TODO must reference a ticket: `// TODO(PROJ-123): migrate to new API`
- CI can report TODO count as a metric — track over time.
- TODOs without tickets are not allowed in PR review.
- FIXMEs indicate bugs — treat as higher priority than TODOs.

---

## Dead Code Detection

- **TypeScript:** `noUnusedLocals: true`, `noUnusedParameters: true` in tsconfig.
- **`ts-prune`**: finds unused exports across the project. Run periodically.
- **ESLint:** `@typescript-eslint/no-unused-vars` with `argsIgnorePattern: '^_'`.
- **Barrel files:** Never re-export symbols that aren't consumed. Check with `ts-prune`.
- After refactoring: grep for old function/component names to ensure no dead references.

---

## Component Documentation (TSDoc)

### Shared Components (`components/ui/`)

Every exported component's props interface must have TSDoc:

```tsx
/**
 * Primary action button with loading state support.
 *
 * @example
 * ```tsx
 * <Button variant="destructive" isLoading={isSubmitting}>
 *   Delete Account
 * </Button>
 * ```
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style variant */
  variant?: ButtonVariant
  /** Size preset */
  size?: ButtonSize
  /** Shows spinner and disables interaction */
  isLoading?: boolean
  /** Render as a child element (Radix Slot pattern) */
  asChild?: boolean
}
```

### Rules
- Document **shared/public** components — not internal/private ones.
- `@example` with a realistic usage snippet.
- `@param` descriptions for non-obvious props.
- `@default` for optional props with defaults.
- These feed Storybook autodocs and IDE tooltips.

### Feature Documentation

- **README per feature** only when non-obvious domain logic or integration exists.
- **ADRs** (`docs/adr/NNNN-title.md`) for significant architectural decisions:
  - Why Zustand over Redux
  - Why next-intl over react-i18next
  - Why Vercel-style over FSD
  - Template: Context, Decision, Consequences

---

## Memory Leak Prevention

### useEffect Cleanup (mandatory)

```tsx
useEffect(() => {
  const controller = new AbortController()

  fetch('/api/data', { signal: controller.signal })
    .then(res => res.json())
    .then(setData)

  return () => controller.abort()  // ← CLEANUP
}, [])
```

### Common Leak Sources

| Source | Prevention |
|--------|-----------|
| `fetch` without abort | Always use `AbortController` with `signal` |
| `addEventListener` | Remove in cleanup: `return () => el.removeEventListener(...)` |
| `setInterval` / `setTimeout` | Clear in cleanup: `return () => clearInterval(id)` |
| `IntersectionObserver` | Disconnect: `return () => observer.disconnect()` |
| `ResizeObserver` | Disconnect: `return () => observer.disconnect()` |
| `WebSocket` | Close: `return () => ws.close()` |
| `EventSource` (SSE) | Close: `return () => source.close()` |
| Module-level state | Never store component references in module-level variables |

### React 19 Ref Cleanup

```tsx
// React 19: ref callbacks can return cleanup functions
<div ref={(node) => {
  const observer = new IntersectionObserver(callback)
  if (node) observer.observe(node)
  return () => observer.disconnect()  // ← Cleanup on unmount
}} />
```

---

## Environment Validation

Validate all environment variables at build time, not runtime:

```ts
// env.ts (loaded at build time)
import { z } from 'zod'

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  NEXT_PUBLIC_API_URL: z.string().url(),
  SESSION_SECRET: z.string().min(32),
  SENTRY_DSN: z.string().url().optional(),
  NODE_ENV: z.enum(['development', 'production', 'test']),
})

export const env = envSchema.parse(process.env)

// Use `env.DATABASE_URL` instead of `process.env.DATABASE_URL`
// Type-safe and validated
```

Or use `@t3-oss/env-nextjs` for the same with client/server separation:

```ts
import { createEnv } from '@t3-oss/env-nextjs'

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    SESSION_SECRET: z.string().min(32),
  },
  client: {
    NEXT_PUBLIC_API_URL: z.string().url(),
  },
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    SESSION_SECRET: process.env.SESSION_SECRET,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
})
```

---

## Virtual Scrolling

For lists with 100+ items, use `@tanstack/react-virtual`:

```tsx
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,  // estimated row height
  })

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: virtualRow.start,
              height: virtualRow.size,
              width: '100%',
            }}
          >
            <ItemRow item={items[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Rule:** Never render 1000+ DOM nodes. Use virtual scrolling for long lists.
