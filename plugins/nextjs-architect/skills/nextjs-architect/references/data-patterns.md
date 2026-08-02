# Data Patterns

## Data Access Layer (DAL)

At scale, never call the database directly from Server Components. Use a Data Access
Layer that enforces authorization and provides a stable API.

### Pattern

```ts
// shared/lib/dal.ts
import 'server-only'
import { cache } from 'react'
import { cookies } from 'next/headers'
import { verifySession } from './auth'
import { db } from './db'

// Memoized per-request via React cache()
export const getCurrentUser = cache(async () => {
  const cookieStore = await cookies()
  const session = await verifySession(cookieStore.get('session')?.value)
  if (!session) return null
  return db.user.findUnique({ where: { id: session.userId } })
})

// DAL function with authorization
export async function getProduct(id: string) {
  const product = await db.product.findUnique({ where: { id } })
  if (!product) return null
  // Public data — no auth check needed
  return product
}

export async function getUserOrders() {
  const user = await getCurrentUser()
  if (!user) throw new Error('Unauthorized')
  return db.order.findMany({ where: { userId: user.id } })
}
```

### Rules
- Mark DAL files with `import 'server-only'` — prevents accidental client import.
- Use `React.cache()` for request-level memoization (e.g., `getCurrentUser` called in
  layout + page runs only once per request).
- Enforce authorization in the DAL, not in components — components call `getUserOrders()`,
  they don't check permissions.
- Keep DAL in `shared/lib/` or `entities/<name>/` depending on scope.

---

## generateStaticParams

Pre-render pages at build time for known parameter sets.

### Product Pages

```tsx
// app/products/[id]/page.tsx
import { db } from '@/shared/lib/db'
import { getProduct } from '@/shared/lib/dal'
import { notFound } from 'next/navigation'

export async function generateStaticParams() {
  const products = await db.product.findMany({ select: { id: true } })
  return products.map(p => ({ id: p.id }))
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const product = await getProduct(id)
  if (!product) return {}
  return {
    title: product.name,
    description: product.description,
    openGraph: { images: [product.imageUrl] },
  }
}

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const product = await getProduct(id)
  if (!product) notFound()

  return (
    <article>
      <h1>{product.name}</h1>
      {/* ... */}
    </article>
  )
}
```

### Locale Pages (with i18n)

```tsx
// app/[locale]/page.tsx
export async function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'ru' }, { locale: 'zh' }]
}
```

### Rules
- Use `generateStaticParams` for pages with a known set of parameters (product catalogs,
  blog posts, locale pages).
- Combine with `dynamicParams = false` to return 404 for unknown params.
- Combine with `revalidate` for ISR (see below).

---

## Incremental Static Regeneration (ISR)

Serve static pages but revalidate them in the background.

### Next.js 15

```tsx
// app/products/[id]/page.tsx
export const revalidate = 3600  // Revalidate every hour

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const product = await fetch(`https://api.example.com/products/${id}`, {
    next: { revalidate: 3600 },
  }).then(r => r.json())

  return <ProductView product={product} />
}
```

### `"use cache"` Restrictions

**Never call `cookies()`, `headers()`, or other request-scoped functions inside `"use cache"`.**
They cause a runtime error because cached functions are detached from the request context.
Read request data outside and pass as arguments:

```tsx
// WRONG — runtime error
async function getProfile() {
  'use cache'
  const cookieStore = await cookies()  // ❌ Fails inside "use cache"
  // ...
}

// CORRECT — pass as argument
async function getProfile(sessionToken: string) {
  'use cache'
  cacheLife('minutes')
  return db.user.findUnique({ where: { sessionToken } })
}

// Caller reads cookies outside the cache boundary
const cookieStore = await cookies()
const token = cookieStore.get('session')?.value
const profile = await getProfile(token)
```

### Next.js 16+

```tsx
import { cacheLife, cacheTag } from 'next/cache'

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  'use cache'
  const { id } = await params
  cacheLife('hours')
  cacheTag(`product-${id}`)

  const product = await getProduct(id)
  return <ProductView product={product} />
}
```

Revalidate after mutations (separate file):

```tsx
// features/product/update-product.action.ts
'use server'
import { revalidateTag } from 'next/cache'
import { db } from '@/shared/lib/db'

export async function updateProductAction(id: string, data: FormData) {
  await db.product.update({ where: { id }, data: Object.fromEntries(data) })
  revalidateTag(`product-${id}`)
}
```

---

## Connection Pooling

Serverless environments (Vercel, AWS Lambda) create a new database connection per
invocation. Without pooling, the database runs out of connections.

### Solutions

| Approach | When to use |
|----------|------------|
| **Prisma Accelerate** | Prisma projects on Vercel — managed connection pool |
| **Neon serverless driver** | Neon Postgres — WebSocket-based, no TCP connection needed |
| **PgBouncer** | Self-hosted — external connection pooler |
| **Drizzle + `@neondatabase/serverless`** | Drizzle ORM with Neon |

### Prisma Example

```ts
// shared/lib/db.ts
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient }

export const db = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db
```

The `globalThis` pattern prevents creating new PrismaClient instances on every hot
reload in development.

### Rules
- Always use a connection pooler in serverless/edge deployments.
- Use the `globalThis` singleton pattern for Prisma in development.
- Set `connection_limit` in your DATABASE_URL for serverless: `?connection_limit=1`.
- For edge runtime: use HTTP-based database drivers (Neon serverless, PlanetScale serverless).

---

## React 19: use() Hook

The `use()` hook reads resources (promises, contexts) during render. Key pattern for
Server-to-Client data passing without `useEffect`.

### Passing a Promise from Server to Client

```tsx
// page.tsx — Server Component
import { Suspense } from 'react'
import { getRecommendations } from '@/shared/lib/dal'
import { RecommendationList } from '@/features/recommendations'
import { RecommendationsSkeleton } from '@/shared/ui/skeletons'
import type { Product } from '@/entities/product'

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  // Start fetching on the server, don't await
  const recommendationsPromise = getRecommendations(id)

  return (
    <div>
      <h1>Product</h1>
      {/* Pass the promise to client — it will suspend until resolved */}
      <Suspense fallback={<RecommendationsSkeleton />}>
        <RecommendationList dataPromise={recommendationsPromise} />
      </Suspense>
    </div>
  )
}

// RecommendationList.tsx — Client Component
'use client'
import { use } from 'react'

// Product type imported from your entities
import type { Product } from '@/entities/product'

export function RecommendationList({ dataPromise }: { dataPromise: Promise<Product[]> }) {
  const recommendations = use(dataPromise)  // Suspends until resolved

  return (
    <ul>
      {recommendations.map(r => <li key={r.id}>{r.name}</li>)}
    </ul>
  )
}
```

### Rules
- `use()` can be called conditionally (unlike other hooks).
- Wrap in `<Suspense>` — `use()` will suspend the component until the promise resolves.
- Pass promises from Server to Client for streaming data without waterfalls.
- Use `use(Context)` as a replacement for `useContext()` — it works the same way.

---

## State Management at Scale

### When to Use What

| State type | < 5 components | 5-20 components | 20+ components |
|-----------|---------------|-----------------|----------------|
| Simple UI toggle | `useState` | `useState` | `useState` |
| Shared UI state (2-3 consumers) | React Context + `useReducer` | React Context | Zustand |
| Complex UI state (theme, sidebar, cart) | Context is fine | Zustand | Zustand |
| Async server state | Server Components | TanStack Query | TanStack Query |
| URL state (filters, pagination) | `searchParams` | `nuqs` | `nuqs` |
| Form state | `useActionState` | `useActionState` | `useActionState` + react-hook-form |

### Zustand Store Structure

```ts
// stores/cart.ts — one store per domain concept
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface CartState {
  items: CartItem[]
  addItem: (item: CartItem) => void
  removeItem: (id: string) => void
  clear: () => void
}

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      addItem: (item) => set((s) => ({ items: [...s.items, item] })),
      removeItem: (id) => set((s) => ({ items: s.items.filter(i => i.id !== id) })),
      clear: () => set({ items: [] }),
    }),
    { name: 'cart-storage' }
  )
)
```

**Rules:**
- One store per domain concept (cart, theme, sidebar) — not one global store.
- Use `persist` middleware for data that survives page reload (cart, preferences).
- Use selectors to minimize re-renders: `useCartStore(s => s.items.length)`.
- Never put server data in Zustand — use Server Components or TanStack Query.

---

## Typed API Clients

For projects that call external APIs (not just database):

### tRPC (full-stack TypeScript, same monorepo)

Best when backend and frontend share a repo. Type-safe end-to-end without code generation.

### openapi-typescript + openapi-fetch (external APIs with OpenAPI spec)

```bash
npx openapi-typescript https://api.example.com/openapi.json -o src/lib/api/schema.d.ts
```

```ts
import createClient from 'openapi-fetch'
import type { paths } from './schema'

const client = createClient<paths>({ baseUrl: 'https://api.example.com' })

const { data, error } = await client.GET('/products/{id}', {
  params: { path: { id: '123' } },
})
// data is fully typed from the OpenAPI spec
```

### orval (OpenAPI → typed React Query hooks)

Generates TanStack Query hooks from OpenAPI spec. Use when the backend provides OpenAPI.

### Rules
- Always type API responses. Never use `any` for API data.
- Validate responses at runtime with Zod when calling untrusted external APIs.
- Use Server Components or Route Handlers as proxy for external APIs — never expose
  API keys to the client.

---

## Auth Library Integration

For most projects, use an auth library instead of building from scratch:

| Library | Best for | Session storage |
|---------|----------|----------------|
| **Auth.js (NextAuth v5)** | OAuth providers, built-in adapters | JWT or database |
| **Clerk** | Managed auth, fast setup | Clerk-hosted |
| **Lucia** | Self-hosted, full control | Database |
| **Supabase Auth** | Supabase projects | Supabase |

**Rules:**
- Session tokens in HTTP-only cookies — never localStorage.
- Middleware for UX redirects only (not security boundary — see `references/forms-auth.md`).
- Verify session in DAL/Server Actions independently.
- Use the library's middleware adapter when available.

> **Note on `"use cache"`:** This directive is experimental/canary in Next.js 15 and expected
> to be stable in Next.js 16. If using Next.js 15 stable, use `fetch()` with `revalidate`
> option or `unstable_cache` instead. Check your Next.js version before using.
