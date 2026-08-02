# SEO, Metadata & Scripts

## Metadata API

### Static Metadata

```tsx
// app/(marketing)/about/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About Us',
  description: 'Learn about our company and mission.',
  openGraph: {
    title: 'About Us',
    description: 'Learn about our company and mission.',
    images: ['/og/about.png'],
  },
  twitter: {
    card: 'summary_large_image',
  },
}
```

### Dynamic Metadata

```tsx
// app/products/[id]/page.tsx
import type { Metadata } from 'next'
import { getProduct } from '@/shared/lib/dal'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params
  const product = await getProduct(id)

  if (!product) return { title: 'Product Not Found' }

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [product.imageUrl],
      type: 'website',
    },
    alternates: {
      canonical: `/products/${id}`,
    },
  }
}
```

### Root Layout Metadata

```tsx
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  metadataBase: new URL('https://example.com'),
  title: {
    template: '%s | My App',   // Child pages: "About | My App"
    default: 'My App',         // Fallback
  },
  description: 'My awesome application.',
  robots: { index: true, follow: true },
}
```

---

## Structured Data (JSON-LD)

### Product Page

```tsx
// app/products/[id]/page.tsx
export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const product = await getProduct(id)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.imageUrl,
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: 'USD',
      availability: product.inStock
        ? 'https://schema.org/InStock'
        : 'https://schema.org/OutOfStock',
    },
  }

  return (
    <>
      {/* dangerouslySetInnerHTML is safe here: JSON.stringify produces no HTML.
         Only use this pattern for JSON-LD with controlled data — never with user HTML. */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article>{/* product content */}</article>
    </>
  )
}
```

### Organization (Root Layout)

```tsx
// app/layout.tsx
const orgJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'My Company',
  url: 'https://example.com',
  logo: 'https://example.com/logo.png',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }}
        />
        {children}
      </body>
    </html>
  )
}
```

---

## sitemap.ts & robots.ts

### Dynamic Sitemap

```ts
// app/sitemap.ts
import type { MetadataRoute } from 'next'
import { db } from '@/shared/lib/db'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const products = await db.product.findMany({ select: { id: true, updatedAt: true } })

  const productUrls = products.map(p => ({
    url: `https://example.com/products/${p.id}`,
    lastModified: p.updatedAt,
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }))

  return [
    { url: 'https://example.com', lastModified: new Date(), priority: 1.0 },
    { url: 'https://example.com/about', priority: 0.5 },
    ...productUrls,
  ]
}
```

### Robots

```ts
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: '*', allow: '/', disallow: ['/api/', '/dashboard/'] },
    ],
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

---

## next/script — Third-Party Scripts

Use `next/script` for analytics, chat widgets, and other third-party scripts.
Never use raw `<script>` tags.

```tsx
// app/layout.tsx
import Script from 'next/script'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}

        {/* Analytics — load after page is interactive */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=GA_ID"
          strategy="afterInteractive"
        />
        <Script id="gtag-init" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'GA_ID');
          `}
        </Script>

        {/* Chat widget — load when browser is idle */}
        <Script
          src="https://widget.intercom.io/widget/APP_ID"
          strategy="lazyOnload"
        />
      </body>
    </html>
  )
}
```

### Strategy Guide

| Strategy | When to use |
|----------|------------|
| `beforeInteractive` | Critical scripts (polyfills, consent managers) — blocks hydration |
| `afterInteractive` | Analytics, tag managers — loads after hydration |
| `lazyOnload` | Chat widgets, social embeds — loads when idle |
| `worker` | Offload to web worker (experimental) |

### Rules
- Always use `next/script` — it handles loading strategy and deduplication.
- Use `strategy="afterInteractive"` for analytics (default).
- Use `strategy="lazyOnload"` for non-critical widgets.
- Place in `layout.tsx` for site-wide scripts, in `page.tsx` for page-specific.
- For inline scripts, use the `id` prop for deduplication.
