# Error Boundaries & Suspense Patterns

## Error Boundaries (error.tsx)

Every route segment that fetches data should have an `error.tsx` file.

### Basic error.tsx

```tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### Key Concepts

- `error.tsx` must be a Client Component (`"use client"`).
- It catches errors in the route segment and all its children.
- The `reset()` function re-renders the segment without a full page reload.
- `error.digest` is a hash for server-side error tracking (don't show to users).

### global-error.tsx

Catches errors in the root layout (which `error.tsx` cannot):

```tsx
'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <h1>Something went wrong</h1>
        <button onClick={reset}>Try again</button>
      </body>
    </html>
  )
}
```

Must include `<html>` and `<body>` tags — it replaces the root layout.

### Nested Error Boundaries

```
app/
  error.tsx              # Catches errors in all child routes
  dashboard/
    error.tsx            # Catches errors in dashboard, NOT parent
    settings/
      error.tsx          # Catches only settings errors
      page.tsx
```

Errors bubble up to the nearest `error.tsx`. Place them strategically:
- Root: generic fallback
- Feature routes: feature-specific error UI with recovery actions

### not-found.tsx

For 404 handling, use `not-found.tsx` (not `error.tsx`):

```tsx
// app/dashboard/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>The requested resource does not exist.</p>
    </div>
  )
}
```

Trigger with `notFound()` from `next/navigation` in Server Components.

---

## Suspense Patterns

### loading.tsx — Route-Level Suspense

`loading.tsx` is syntactic sugar for wrapping `page.tsx` in `<Suspense>`:

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <DashboardSkeleton />
}
```

### Manual Suspense — Granular Streaming

For progressive loading within a page, use `<Suspense>` directly:

```tsx
// page.tsx — Server Component
import { Suspense } from 'react'

export default async function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Shell loads immediately */}
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel />  {/* Streams when data is ready */}
      </Suspense>

      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />  {/* Streams independently */}
      </Suspense>

      <Suspense fallback={<TableSkeleton />}>
        <RecentOrders />  {/* Streams independently */}
      </Suspense>
    </div>
  )
}
```

Each `<Suspense>` boundary streams independently. The user sees a progressive loading
experience: shell first, then each section as its data arrives.

### Nested Suspense for Prioritized Loading

```tsx
<Suspense fallback={<PageSkeleton />}>
  <Header />  {/* Loads first — part of outer boundary */}

  <Suspense fallback={<ContentSkeleton />}>
    <MainContent />  {/* Loads second */}

    <Suspense fallback={<SidebarSkeleton />}>
      <Sidebar />  {/* Loads last — lowest priority */}
    </Suspense>
  </Suspense>
</Suspense>
```

### Rules
- Every async Server Component should be wrapped in `<Suspense>`.
- Use meaningful skeleton components as fallbacks — not spinners.
- Place `<Suspense>` boundaries based on data dependencies, not visual layout.
- Combine `<Suspense>` with `error.tsx` — errors in a Suspense boundary are caught
  by the nearest `error.tsx`.
- Use `loading.tsx` for route-level loading, manual `<Suspense>` for within-page streaming.
