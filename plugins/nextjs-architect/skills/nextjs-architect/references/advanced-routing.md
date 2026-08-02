# Advanced Routing Patterns

## Parallel Routes (@slot)

Parallel routes render multiple pages simultaneously in the same layout using named
slots. Essential for dashboards, split views, and modals.

### Setup

```
app/
  @analytics/
    page.tsx              # Analytics slot
    loading.tsx
    default.tsx           # REQUIRED — fallback for unmatched routes
  @activity/
    page.tsx              # Activity slot
    default.tsx           # REQUIRED
  layout.tsx              # Renders both slots
  page.tsx                # Main content
```

### Layout

```tsx
// app/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  activity,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  activity: React.ReactNode
}) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <main className="col-span-2">{children}</main>
      <aside>
        {analytics}
        {activity}
      </aside>
    </div>
  )
}
```

### default.tsx

**Every parallel route must have a `default.tsx`** — Next.js uses it as the fallback
when a slot doesn't match the current URL during soft navigation. Without it, the
build fails or the slot renders nothing.

```tsx
// app/@analytics/default.tsx
export default function Default() {
  return null  // Or a fallback UI
}
```

---

## Intercepting Routes

Intercept a route to show it in a different context (e.g., modal overlay) while
preserving the original URL. Uses `(.)`, `(..)`, `(...)` conventions.

### Photo Gallery Modal Pattern

```
app/
  @modal/
    (.)photos/[id]/       # Intercepts /photos/[id] — shows in modal
      page.tsx
    default.tsx
  photos/
    [id]/
      page.tsx             # Full page — accessed on direct navigation or refresh
  layout.tsx
  page.tsx
```

### Modal Implementation

```tsx
// app/@modal/(.)photos/[id]/page.tsx — Modal view
import { Modal } from '@/shared/ui/Modal'
import { getPhoto } from '@/entities/photo'

export default async function PhotoModal({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const photo = await getPhoto(id)

  return (
    <Modal>
      <img src={photo.url} alt={photo.alt} />
      <p>{photo.description}</p>
    </Modal>
  )
}
```

```tsx
// app/photos/[id]/page.tsx — Full page view (direct navigation / refresh)
import { getPhoto } from '@/entities/photo'

export default async function PhotoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const photo = await getPhoto(id)

  return (
    <article>
      <img src={photo.url} alt={photo.alt} />
      <p>{photo.description}</p>
    </article>
  )
}
```

### Interception Conventions

| Convention | Intercepts |
|-----------|-----------|
| `(.)` | Same level |
| `(..)` | One level up |
| `(..)(..)` | Two levels up |
| `(...)` | From root `app/` |

### Common Use Cases
- Photo/product modals in galleries (Instagram-style)
- Login/signup modals overlaying content
- Quick-view cards in dashboards
- Shopping cart drawer intercepting `/cart`

---

## template.tsx vs layout.tsx

`layout.tsx` persists across navigations (shared state preserved).
`template.tsx` re-mounts on every navigation (fresh state each time).

### When to Use template.tsx

```tsx
// app/(dashboard)/template.tsx
export default function DashboardTemplate({
  children,
}: {
  children: React.ReactNode
}) {
  // This runs on EVERY navigation, unlike layout.tsx
  return (
    <div>
      {/* Page transition animations (ViewTransition is experimental — check React docs) */}
      {/* import { unstable_ViewTransition as ViewTransition } from 'react' */}
      {children}
    </div>
  )
}
```

| Use Case | layout.tsx | template.tsx |
|----------|-----------|-------------|
| Persistent navigation/sidebar | Yes | No |
| Page enter/exit animations | No | Yes |
| Per-page analytics logging | No | Yes |
| Form state reset on route change | No | Yes |
| Shared providers | Yes | No |

---

## Partial Prerendering (PPR)

PPR serves a static shell immediately, then streams dynamic content into Suspense holes.
Combines the speed of static with the freshness of dynamic — best of both worlds.

### Enable (Next.js 15)

```ts
// next.config.ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  experimental: {
    ppr: true,  // Next.js 15: experimental
  },
}

export default config
```

In Next.js 16+, PPR is expected to be stable — check release notes.

### How It Works

```tsx
// page.tsx
import { Suspense } from 'react'

export default function ProductPage() {
  return (
    <div>
      {/* STATIC SHELL — served from CDN instantly */}
      <Header />
      <ProductInfo />

      {/* DYNAMIC HOLES — streamed via Suspense */}
      <Suspense fallback={<PriceSkeleton />}>
        <LivePrice />  {/* Real-time pricing — dynamic */}
      </Suspense>

      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews />  {/* User-specific — dynamic */}
      </Suspense>
    </div>
  )
}
```

### Rules
- Static parts render at build time (or on first request) and are cached at the edge.
- Dynamic parts are wrapped in `<Suspense>` and streamed on each request.
- No code changes needed beyond proper Suspense boundaries — PPR works automatically.
- Combine with `cacheLife()` / `cacheTag()` to control which parts are static vs dynamic.

---

## Route Groups for Layout Segmentation

Route groups `(name)` organize routes without affecting the URL, and importantly,
control which layout applies.

### Different Layouts for Different Sections

```
app/
  (marketing)/           # Marketing layout — no sidebar, hero headers
    layout.tsx
    page.tsx             # / (home)
    about/page.tsx       # /about
    pricing/page.tsx     # /pricing
  (dashboard)/           # Dashboard layout — sidebar, authenticated
    layout.tsx
    overview/page.tsx    # /overview
    settings/page.tsx    # /settings
  (auth)/                # Minimal layout — centered card
    layout.tsx
    login/page.tsx       # /login
    register/page.tsx    # /register
```

### Rules
- Route groups create layout boundaries — each group can have its own `layout.tsx`.
- Group names are for organization only — `(marketing)/about` maps to `/about`, not `/marketing/about`.
- Use for: public vs authenticated areas, different visual layouts, feature isolation.
- Each group can have its own `error.tsx`, `loading.tsx`, and `not-found.tsx`.
