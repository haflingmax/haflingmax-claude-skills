# Component Patterns

## Hook + View Separation

For components with significant logic (>1 `useState`, any `useEffect`, complex handlers),
split into:
- **Hook** (`useComponentName.ts`) — state, effects, handlers, data transforms
- **View** (`ComponentName.tsx`) — pure JSX, styling, accessibility

Skip separation for: pure presentational components, Server Components with only a data
fetch, components under ~20 lines.

### Example

```tsx
// useProductCard.ts — LOGIC
'use client'
import { useOptimistic } from 'react'
import { addToCartAction } from '@/features/add-to-cart'
import { formatPrice } from '@/shared/lib/format'
import type { Product } from '@/entities/product'

export function useProductCard(product: Product) {
  const [optimisticStock, setOptimisticStock] = useOptimistic(
    product.stock,
    (current: number, delta: number) => current + delta
  )

  const handleAddToCart = async () => {
    setOptimisticStock(-1)
    await addToCartAction(product.id)
  }

  return {
    name: product.name,
    price: formatPrice(product.price),
    stock: optimisticStock,
    isOutOfStock: optimisticStock <= 0,
    onAddToCart: handleAddToCart,
  }
}
```

```tsx
// ProductCard.tsx — CLIENT Component (uses client hook)
'use client'
import styles from './ProductCard.module.css'
import { useProductCard } from './useProductCard'
import type { Product } from '@/entities/product'

export function ProductCard({ product }: { product: Product }) {
  const vm = useProductCard(product)

  return (
    <article className={styles.card}>
      <h3>{vm.name}</h3>
      <span>{vm.price}</span>
      <button onClick={vm.onAddToCart} disabled={vm.isOutOfStock}>
        Add to Cart
      </button>
    </article>
  )
}
```

### Server Components — Data IS the Logic

No hooks needed. The data fetch IS the component:

```tsx
// ProductList.tsx — Server Component
import { Suspense } from 'react'
import { cacheLife, cacheTag } from 'next/cache'  // Next.js 16+
import { db } from '@/shared/lib/db'
import { ProductCard } from '@/entities/product'
import styles from './ProductList.module.css'

export async function ProductList() {
  'use cache'  // Next.js 16+ only. For 15, use fetch() with revalidate option.
  cacheLife('minutes')
  cacheTag('products')

  const products = await db.products.findMany({ orderBy: { createdAt: 'desc' } })

  return (
    <section className={styles.grid}>
      {products.map(p => <ProductCard key={p.id} product={p} />)}
    </section>
  )
}
```

---

## File Grouping Rules

**Core principle:** Colocate files that change together (Dodds, Abramov, Next.js docs).
Extract to shared only when a second consumer appears.

### Rule 1: Group When 2+ Files Belong Together

A component with its hook + test = 3 files → own subfolder. Always.
A single-file component (Divider, Icon) can stay flat.

### Rule 2: Domain Grouping

Group components by **business domain**, not technical type. This applies to
both Vercel-style (`components/{domain}/`) and FSD-style (`features/{domain}/`).

**Vercel-style (default):**
```
components/
  chat/                        # Domain: chat feature
    ChatPanel.tsx              # View
    useChatPanel.ts            # Logic hook
    ChatPanel.test.tsx         # Test
    ChatMessage.tsx            # Sub-component
    ChatInput.tsx
  dashboard/
    StatsPanel.tsx
    useStatsPanel.ts
    RevenueChart.tsx
  settings/
    Settings.tsx               # Tab switcher view
    ProfileTab.tsx             # Sub-view
    useProfileTab.ts           # Tab-specific hook
    SecurityTab.tsx
  auth/                        # Related pages grouped
    LoginForm.tsx
    RegisterForm.tsx
    VerifyEmailForm.tsx
    useAuth.ts                 # Shared auth hook
  ui/                          # shadcn primitives
    button.tsx, input.tsx, dialog.tsx
```

**FSD-style (large apps):**
```
features/
  chat/
    ChatPanel.tsx, useChatPanel.ts, ChatPanel.test.tsx
  auth/
    LoginForm.tsx, RegisterForm.tsx, useAuth.ts
entities/
  product/
    ProductCard.tsx, useProduct.ts, product.types.ts
shared/
  ui/
    Button/, Input/, Modal/
  hooks/
    useDebounce.ts, useMediaQuery.ts
```

### Rule 3: Hook Placement (colocation)

| Scope | Location |
|-------|----------|
| Component-specific (1 consumer) | Next to component: `components/chat/useChatPanel.ts` |
| Domain-shared (2+ in same domain) | Domain root: `components/auth/useAuth.ts` |
| App-wide (2+ unrelated consumers) | `hooks/useDebounce.ts` or `shared/hooks/` |

**Never put a component-specific hook in the global `hooks/` directory.**

### Rule 4: Server Actions Placement

| Pattern | Location |
|---------|----------|
| Route-scoped actions | `app/(feature)/actions.ts` — colocated with route group |
| Feature-scoped actions | `components/chat/actions.ts` or `features/chat/actions.ts` |
| Shared mutation logic | `lib/db/queries.ts` (DAL) |

### Rule 5: Related Pages → Single Folder

Pages sharing a domain concept group together:
- `auth/` → Login, Register, VerifyEmail, ForgotPassword
- `settings/` → ProfileTab, SecurityTab, NotificationsTab
- `products/` → ProductList, ProductDetail, ProductEdit

### Rule 6: Max 3-4 Levels of Nesting

Per React docs recommendation. If deeper, restructure.

Sources: Kent C. Dodds (Colocation), Bulletproof React (alan2207), Josh Comeau
(File Structure), Next.js docs (Route Groups, Private Folders), Vercel AI Chatbot,
Robert C. Martin (Screaming Architecture).

---

## Component File Structure

**ui/ components with states/variants MUST have their own subfolder** — not dumped flat.
`button.tsx`, `input.tsx`, `select.tsx` as flat files in `ui/` is an anti-pattern when
they have variants, tests, and stories. Only truly trivial components (Separator, Badge
without interaction) can stay as single files.

```
ComponentName/
  ComponentName.types.ts    # Separate file when >5 lines of types
  ComponentName.tsx         # View (may include types inline if simple)
  useComponentName.ts       # Hook (only if significant state/effects)
  ComponentName.module.css  # Styles (or Tailwind in TSX)
  ComponentName.test.tsx    # Tests (Vitest + RTL)
  ComponentName.stories.tsx # Story (if Storybook present)
  index.ts                  # Selective re-export
```

### Types Example

```ts
// Button.types.ts (when types are complex enough)
export type ButtonVariant = 'primary' | 'secondary' | 'destructive'
export type ButtonSize = 'sm' | 'md' | 'lg'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  isLoading?: boolean
  ref?: React.Ref<HTMLButtonElement>  // React 19: ref as regular prop
}
```

---

## Implementation Rules

- **Named exports** only. Exception: Next.js convention files that require default export
  (`page.tsx`, `layout.tsx`, `error.tsx`, `loading.tsx`, `not-found.tsx`, `default.tsx`,
  `template.tsx`, `global-error.tsx`, `route.ts`).
- **`ref` as a regular prop** (React 19+). Use `forwardRef` only for React 18 support.
  Ref callbacks can now return a cleanup function — don't return other values.
- **Discriminated unions** for mutually exclusive prop combinations.
- **No inline styles.** Match project's styling approach.
- **Prop spreading:** Destructure explicitly. Exception: headless UI libraries (Radix,
  Headless UI) and form libraries (React Hook Form `register()`) that provide spread
  props by design.
- **No `any`.** Use `unknown` + type guards.
- **No `JSX.Element` return type.** Removed in React 19. Use `React.JSX.Element` or
  (preferred) let TypeScript infer the return type.
- **No `defaultProps` on function components.** Removed in React 19 (silently ignored).
  Use ES6 default parameters: `function Button({ size = 'md' }: ButtonProps)`.
- **No `typeof window !== 'undefined'` in render.** Causes hydration mismatch.
  Use `useEffect` for client-only logic.

---

## Storybook

CSF3 format. Every new component gets a `.stories.tsx` if Storybook is present.

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { expect, userEvent, within } from '@storybook/test'
import { Button } from './Button'

const meta = {
  component: Button,
  tags: ['autodocs'],
} satisfies Meta<typeof Button>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: { variant: 'primary', children: 'Click me' },
}

export const WithInteraction: Story = {
  args: { children: 'Submit' },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await userEvent.click(canvas.getByRole('button'))
    await expect(canvas.getByRole('button')).toHaveFocus()
  },
}
```

Use `@storybook/nextjs-vite` (8.5+) or `@storybook/nextjs` (Webpack, existing setups).

---

## Testing

| Layer | Tool | Target |
|-------|------|--------|
| Unit | Vitest | Hooks, utilities, Server Action validation logic |
| Component | Vitest + RTL | Rendering, interactions, a11y |
| E2E | Playwright | Full flows, Server Components, auth |

- Query by `getByRole` — tests accessibility simultaneously.
- `userEvent` (not `fireEvent`).
- Test behavior, not implementation.
- Use MSW (Mock Service Worker) for API mocking.
- Server Components: test data-fetching functions as unit tests, Playwright for integration.
- Server Actions: test validation as pure functions, side effects via E2E.
