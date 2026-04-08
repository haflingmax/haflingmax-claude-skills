# Form Handling & Authentication Patterns

## Server Action Form Pattern

The complete pattern for forms with Server Actions, validation, error display,
and progressive enhancement.

### 1. Define the Server Action

```tsx
// features/contact/contact.action.ts
'use server'

import { z } from 'zod'

const ContactSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  email: z.string().email('Invalid email address'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
})

export type ContactState = {
  errors?: Record<string, string[]>
  message?: string
  success?: boolean
}

export async function submitContactAction(
  prevState: ContactState,
  formData: FormData
): Promise<ContactState> {
  // Auth check — Server Actions are public endpoints, anyone can POST
  // For public forms (contact), auth may not be needed — but rate-limit instead.
  // For protected actions, always verify session:
  // const user = await getCurrentUser()
  // if (!user) return { message: 'Unauthorized' }

  const raw = Object.fromEntries(formData)
  const result = ContactSchema.safeParse(raw)

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors }
  }

  try {
    const { db } = await import('@/shared/lib/db')  // Dynamic import to keep action module lean
    await db.contacts.create({ data: result.data })
    return { success: true, message: 'Message sent!' }
  } catch {
    return { message: 'Failed to send. Please try again.' }
  }
}
```

### 2. Build the Form Component

```tsx
// features/contact/ContactForm.tsx
'use client'

import { useActionState } from 'react'
import { useFormStatus } from 'react-dom'
import { submitContactAction, type ContactState } from './contact.action'

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending} aria-busy={pending}>
      {pending ? 'Sending...' : 'Send Message'}
    </button>
  )
}

export function ContactForm() {
  const [state, formAction] = useActionState(submitContactAction, {})

  if (state.success) {
    return <p role="status">{state.message}</p>
  }

  return (
    <form action={formAction} noValidate>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" name="name" required />
        {state.errors?.name && (
          <p role="alert" aria-live="polite">{state.errors.name[0]}</p>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" required />
        {state.errors?.email && (
          <p role="alert" aria-live="polite">{state.errors.email[0]}</p>
        )}
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea id="message" name="message" required />
        {state.errors?.message && (
          <p role="alert" aria-live="polite">{state.errors.message[0]}</p>
        )}
      </div>

      {state.message && !state.success && (
        <p role="alert">{state.message}</p>
      )}

      <SubmitButton />
    </form>
  )
}
```

### 3. With Optimistic UI

```tsx
'use client'

import { useOptimistic } from 'react'

import { likePostAction } from '@/features/likes/like.action'

export function LikeButton({ likes, postId }: { likes: number; postId: string }) {
  const [optimisticLikes, setOptimisticLikes] = useOptimistic(
    likes,
    (current: number, delta: number) => current + delta
  )

  async function handleLike() {
    setOptimisticLikes(1)
    await likePostAction(postId)
  }

  return (
    <form action={handleLike}>
      <button type="submit">{optimisticLikes} Likes</button>
    </form>
  )
}
```

### Form Rules
- Always validate server-side with Zod — client validation is UX, not security.
- Use `useActionState` (React 19) for form state management, not `useState`.
- Use `useFormStatus` for pending states — it reads the nearest parent `<form>`.
- Forms work without JavaScript (progressive enhancement) when using `action`.
- Show field-level errors with `aria-live="polite"` for accessibility.
- Return typed state objects from Server Actions — not throwing errors.

---

## Authentication / Route Protection

### CRITICAL: Middleware is NOT a Security Boundary

Middleware can be bypassed (CVE-2025-29927 via `x-middleware-subrequest` header).
Use middleware for **UX redirects only** (redirect unauthenticated users to login).
Always enforce auth independently in the DAL, Server Actions, and Route Handlers.

> **Every Server Action is a public HTTP endpoint.** Anyone can POST to it directly.
> Always validate authentication inside the action, not just input shape.

### Middleware Pattern (Next.js 15) — UX redirects only

```tsx
// middleware.ts — convenience redirects, NOT security enforcement
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('session')?.value

  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  // Redirect authenticated users away from login
  if (request.nextUrl.pathname === '/login' && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
}
```

### Server Component Auth Check

For data-level authorization (not just route access):

```tsx
// app/(dashboard)/layout.tsx
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { verifySession } from '@/shared/lib/auth'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const cookieStore = await cookies()
  const session = await verifySession(cookieStore.get('session')?.value)

  if (!session) {
    redirect('/login')
  }

  return <>{children}</>
}
```

### Auth Rules
- Use HTTP-only cookies for session tokens — never localStorage.
- Middleware handles route-level access (redirects). Server Components handle data-level
  authorization (what to show).
- Validate sessions on every request in middleware — don't trust client state.
- Use `redirect()` in Server Components for auth failures — it throws, so no code runs after.
- Keep auth logic in `shared/lib/auth.ts` — don't scatter across components.

---

## Route Handlers (API Routes)

Use Route Handlers only when Server Actions are not sufficient:
- Webhooks from external services
- Streaming responses
- Third-party OAuth callbacks
- Public API endpoints

```tsx
// app/api/webhooks/stripe/route.ts
import { NextResponse } from 'next/server'
import { headers } from 'next/headers'

export async function POST(request: Request) {
  const body = await request.text()
  const headersList = await headers()
  const signature = headersList.get('stripe-signature')

  // Verify webhook signature
  // Process event
  // Return response

  return NextResponse.json({ received: true })
}
```

Prefer Server Actions over Route Handlers for form submissions and mutations.

---

## Server Action Limitations

Server Actions have constraints. Use Route Handlers when you hit them:

| Limitation | Workaround |
|-----------|-----------|
| **1MB body size limit** (default) | Increase via `serverActions.bodySizeLimit` in `next.config.ts`, or use Route Handler for large payloads |
| **File uploads >1MB** | Use presigned URLs (S3/R2/GCS) — upload directly from client to storage, then pass the URL to a Server Action |
| **Streaming responses** | Route Handlers with `ReadableStream` |
| **Sequential per form** | For parallel mutations, use multiple forms or Route Handlers |
| **No WebSocket/SSE** | Route Handlers with `ReadableStream` for SSE; external service for WebSocket |

### File Upload Pattern

```tsx
// features/upload/upload.action.ts
'use server'
import { z } from 'zod'
import { generatePresignedUrl } from '@/shared/lib/storage'

const UploadSchema = z.object({
  filename: z.string().min(1),
  contentType: z.string().startsWith('image/'),
})

export async function getUploadUrlAction(input: { filename: string; contentType: string }) {
  const parsed = UploadSchema.parse(input)
  const { url, key } = await generatePresignedUrl(parsed)
  return { uploadUrl: url, fileKey: key }
}
```

```tsx
// features/upload/UploadButton.tsx
'use client'
import { getUploadUrlAction } from './upload.action'

export function UploadButton() {
  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    // 1. Get presigned URL from server
    const { uploadUrl, fileKey } = await getUploadUrlAction({
      filename: file.name,
      contentType: file.type,
    })

    // 2. Upload directly to storage (bypasses Next.js body limit)
    await fetch(uploadUrl, { method: 'PUT', body: file })

    // 3. Save file reference via Server Action
    await saveFileAction(fileKey)
  }

  return <input type="file" accept="image/*" onChange={handleUpload} />
}
```

### Configuring Body Size Limit

```ts
// next.config.ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: '4mb',  // Increase from default 1MB
    },
  },
}

export default config
```
