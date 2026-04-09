# Security Headers & Hardening

Production security requirements beyond auth and input validation.

---

## Security Headers (next.config.ts)

```ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '0' },  // Disable legacy XSS filter
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
        ],
      },
    ]
  },
}

export default config
```

### What Each Header Does

| Header | Purpose |
|--------|---------|
| `X-Content-Type-Options: nosniff` | Prevents MIME type sniffing |
| `X-Frame-Options: DENY` | Prevents clickjacking (embedding in iframe) |
| `Referrer-Policy` | Controls how much URL info is sent on navigation |
| `Permissions-Policy` | Blocks access to browser APIs (camera, mic, location) |
| `Strict-Transport-Security` | Forces HTTPS for 2 years + preload list |
| `X-XSS-Protection: 0` | Disables buggy legacy XSS auditor (modern CSP is better) |

---

## Content Security Policy (CSP)

### Nonce-based CSP (recommended for Next.js)

```ts
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')
  
  const csp = [
    `default-src 'self'`,
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`,
    `style-src 'self' 'unsafe-inline'`,  // Required for Tailwind / CSS-in-JS
    `img-src 'self' blob: data: https:`,
    `font-src 'self'`,
    `connect-src 'self' https://api.example.com`,  // Add your API domains
    `frame-ancestors 'none'`,
    `base-uri 'self'`,
    `form-action 'self'`,
  ].join('; ')

  const response = NextResponse.next()
  response.headers.set('Content-Security-Policy', csp)
  response.headers.set('x-nonce', nonce)
  return response
}
```

Pass the nonce to scripts in the root layout:

```tsx
// app/layout.tsx
import { headers } from 'next/headers'

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const headersList = await headers()
  const nonce = headersList.get('x-nonce') ?? ''

  return (
    <html>
      <body>
        {children}
        <Script nonce={nonce} strategy="afterInteractive" src="..." />
      </body>
    </html>
  )
}
```

---

## Rate Limiting

### Server Actions and Route Handlers

```ts
// shared/lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

export const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),  // 10 requests per 10 seconds
  analytics: true,
})

// Usage in Server Action
'use server'
import { headers } from 'next/headers'
import { ratelimit } from '@/shared/lib/rate-limit'

export async function submitFormAction(prevState: State, formData: FormData) {
  const headersList = await headers()
  const ip = headersList.get('x-forwarded-for') ?? '127.0.0.1'
  
  const { success } = await ratelimit.limit(ip)
  if (!success) {
    return { error: 'Too many requests. Please try again later.' }
  }
  
  // ... process form
}
```

---

## CSRF Protection

- **Server Actions:** Next.js automatically validates `Origin` header against `Host`.
  CVE-2026-27978 showed this can be bypassed from sandboxed iframes (`origin: null`).
  Mitigate: reject requests with `origin: null` in critical actions.
- **Route Handlers:** no automatic CSRF protection. For mutation endpoints,
  validate `Origin` header or use CSRF tokens (e.g., `csrf` package).
- **Cookies:** Set `SameSite=Lax` (default) or `SameSite=Strict` on session cookies.

---

## Dependency Security

- **`npm audit`** in CI pipeline — fail build on critical/high vulnerabilities.
- **Dependabot or Renovate** for automated dependency updates.
- **Lock file integrity:** commit `package-lock.json` / `pnpm-lock.yaml`. CI uses
  `npm ci` (not `npm install`) to respect the lock file.
- **No `*` versions** in package.json — pin exact or use `^` for minor updates.

---

## XSS Prevention

- Never use `dangerouslySetInnerHTML` with user input.
- For JSON-LD structured data: `JSON.stringify` is safe (no HTML injection).
- For markdown rendering: use a sanitizer (`DOMPurify`, `rehype-sanitize`).
- For URL parameters in `href`: validate protocol — never allow `javascript:` URLs.
  ```tsx
  const safeHref = url.startsWith('http') ? url : '#'
  ```

---

## Rules

1. **All headers above are mandatory** for production deployment.
2. CSP nonce regenerated per request (middleware).
3. Rate limit every public Server Action and Route Handler.
4. `npm audit` in CI. Dependabot enabled. Lock file committed.
5. No `dangerouslySetInnerHTML` with user content. Sanitize markdown.
6. Session cookies: `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`.
