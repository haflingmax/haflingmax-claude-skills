# Theming (Light/Dark Mode)

Use `next-themes` for state management + CSS custom properties for styling. This is the
industry standard (shadcn/ui, Vercel, Radix all use this pattern).

## Setup

1. **ThemeProvider** — a single `"use client"` wrapper in root layout. All children stay Server Components.
2. **CSS tokens** — define in `:root` (light) and `.dark` overrides. Use semantic pairs:

```css
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.45 0.2 260);
  --primary-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.577 0.245 27);
  --warning: oklch(0.75 0.18 85);
  --success: oklch(0.6 0.2 145);
  --muted: oklch(0.96 0 0);
  --muted-foreground: oklch(0.55 0 0);
  --border: oklch(0.92 0 0);
  --ring: oklch(0.7 0 0);
  color-scheme: light;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  /* ... override all tokens */
  color-scheme: dark;
}
```

3. **Theme toggle** — only the toggle button needs `"use client"` + `useTheme()`:

```tsx
'use client'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

export function ThemeSwitch() {
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()
  useEffect(() => setMounted(true), [])
  if (!mounted) return null  // Prevent hydration mismatch
  // ... render toggle
}
```

## Rules
- Every color references a CSS custom property — never hardcoded values. OKLCH color
  values are recommended for perceptual uniformity (~92% global browser support as of 2025).
  Add hex fallbacks if targeting older browsers.
- Use semantic token pairs: `--primary` / `--primary-foreground`, `--destructive` / `--destructive-foreground`.
- Add `color-scheme: light` / `dark` to enable native UA element theming.
- Add `suppressHydrationWarning` on `<html>` tag (next-themes injects class before hydration).
- Use `prefers-reduced-motion` media query to respect user preferences.
