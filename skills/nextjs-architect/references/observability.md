# Observability & Monitoring

Production monitoring, error tracking, logging, and feature flags.

---

## Error Tracking (Sentry)

### Setup

```bash
npx @sentry/wizard@latest -i nextjs
```

This creates `sentry.client.config.ts`, `sentry.server.config.ts`, `sentry.edge.config.ts`,
and wraps `next.config.ts` with `withSentryConfig`.

### Key Configuration

```ts
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.replayIntegration(),
    Sentry.feedbackIntegration({ colorScheme: 'system' }),
  ],
})
```

### Error Boundary Integration

```tsx
// app/error.tsx — automatically captured by Sentry
'use client'
import * as Sentry from '@sentry/nextjs'
import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### User Context

```tsx
// After authentication, set user context
Sentry.setUser({ id: user.id, email: user.email })

// On logout
Sentry.setUser(null)
```

### Rules
- Never send PII to Sentry (passwords, tokens). Configure `beforeSend` to strip sensitive data.
- Set `tracesSampleRate` low in production (0.1-0.2) to control costs.
- Use `Sentry.captureMessage` for business-logic warnings (not just errors).
- Tag errors with feature area: `Sentry.setTag('feature', 'checkout')`.

---

## Web Vitals Monitoring

### Next.js Built-in (Vercel)

Vercel Analytics automatically tracks Core Web Vitals. No code needed if on Vercel.

### Custom (self-hosted)

```tsx
// app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next'  // or custom:

// Custom Web Vitals reporter
'use client'
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitalsReporter() {
  useReportWebVitals((metric) => {
    // Send to your analytics endpoint
    fetch('/api/analytics', {
      method: 'POST',
      body: JSON.stringify({
        name: metric.name,       // LCP, CLS, INP, FCP, TTFB
        value: metric.value,
        rating: metric.rating,   // 'good' | 'needs-improvement' | 'poor'
        navigationType: metric.navigationType,
      }),
    })
  })
  return null
}
```

### Thresholds

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| INP | ≤ 200ms | ≤ 500ms | > 500ms |

---

## Structured Logging

### Server-Side (pino)

```ts
// shared/lib/logger.ts
import pino from 'pino'

export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
  // Don't log PII
  redact: ['req.headers.authorization', 'req.headers.cookie', 'email', 'password'],
})
```

### Usage in Server Actions / Route Handlers

```ts
import { logger } from '@/shared/lib/logger'

export async function submitOrderAction(formData: FormData) {
  const orderId = crypto.randomUUID()
  logger.info({ orderId, action: 'submitOrder' }, 'Order submission started')
  
  try {
    // ... process
    logger.info({ orderId }, 'Order submitted successfully')
  } catch (error) {
    logger.error({ orderId, error }, 'Order submission failed')
    throw error
  }
}
```

### Rules
- **Never `console.log` in production code.** Use structured logger.
- JSON format for production (machine-parseable). Human-readable for development.
- Include request ID / correlation ID for tracing across services.
- Redact PII (passwords, tokens, emails) in log configuration.
- Log levels: `error` → production alerting, `warn` → monitoring, `info` → business events,
  `debug` → development only.

---

## Feature Flags

### Vercel Flags / Statsig / LaunchDarkly

```tsx
// middleware.ts — evaluate flags per request
import { NextResponse } from 'next/server'
import { getFlags } from '@/shared/lib/flags'

export async function middleware(request: NextRequest) {
  const flags = await getFlags(request)
  const response = NextResponse.next()
  
  // Pass flags via cookie or header for Server Components to read
  response.cookies.set('feature-flags', JSON.stringify(flags))
  return response
}
```

```tsx
// Server Component reads flags
import { cookies } from 'next/headers'

export default async function CheckoutPage() {
  const cookieStore = await cookies()
  const flags = JSON.parse(cookieStore.get('feature-flags')?.value ?? '{}')
  
  return (
    <div>
      {flags.newCheckoutFlow ? <NewCheckout /> : <LegacyCheckout />}
    </div>
  )
}
```

### Rules
- Evaluate flags in middleware (per-request, before rendering).
- Pass flag values to Server Components via cookies or headers (not client-side SDK).
- Clean up old flags aggressively — dead flags are technical debt.
- Use feature flags for gradual rollouts, A/B tests, and kill switches.

---

## Health Check Endpoint

```ts
// app/api/health/route.ts
import { NextResponse } from 'next/server'
import { db } from '@/shared/lib/db'

export async function GET() {
  try {
    // Check database connectivity
    await db.$queryRaw`SELECT 1`
    
    return NextResponse.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: process.env.APP_VERSION ?? 'unknown',
    })
  } catch {
    return NextResponse.json(
      { status: 'error', message: 'Database unreachable' },
      { status: 503 }
    )
  }
}
```

Used by: Kubernetes readiness probes, load balancers, uptime monitors.
