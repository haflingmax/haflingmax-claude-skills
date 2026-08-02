# Semantic Component Variants

Components that communicate status (alerts, badges, buttons, toasts) use a two-axis system:
**variant** (visual weight) and **intent** (semantic meaning). These are independent axes.

## The Two-Axis Pattern

```tsx
// variant = how much visual attention
type Variant = 'solid' | 'outline' | 'ghost' | 'soft'

// intent = what it communicates
type Intent = 'default' | 'danger' | 'warning' | 'success' | 'info'
```

A ghost button can communicate danger. An outline badge can signal success. The axes don't conflate.

## With CVA (class-variance-authority) — for Tailwind projects

```tsx
import { cva, type VariantProps } from 'class-variance-authority'

const alertVariants = cva(
  'rounded-lg border p-4 flex items-start gap-3',
  {
    variants: {
      intent: {
        default: '',
        danger: '',
        warning: '',
        success: '',
        info: '',
      },
      variant: {
        solid: '',
        soft: '',
        outline: 'bg-transparent',
      },
    },
    compoundVariants: [
      { variant: 'solid', intent: 'danger', class: 'bg-destructive text-destructive-foreground border-destructive' },
      { variant: 'solid', intent: 'warning', class: 'bg-warning text-warning-foreground border-warning' },
      { variant: 'solid', intent: 'success', class: 'bg-success text-success-foreground border-success' },
      { variant: 'soft', intent: 'danger', class: 'bg-destructive/10 text-destructive border-destructive/20' },
      { variant: 'soft', intent: 'warning', class: 'bg-warning/10 text-warning border-warning/20' },
      { variant: 'soft', intent: 'success', class: 'bg-success/10 text-success border-success/20' },
      { variant: 'outline', intent: 'danger', class: 'border-destructive text-destructive' },
      // ... complete the matrix
    ],
    defaultVariants: { variant: 'soft', intent: 'default' },
  }
)

type AlertProps = VariantProps<typeof alertVariants> & { title: string; children: React.ReactNode }
```

## With CSS Modules — for CSS Modules projects

```css
/* Alert.module.css */
.alert { border-radius: var(--radius-md); border: 1px solid; padding: 1rem; display: flex; gap: 0.75rem; }

/* Intents */
.danger { color: var(--color-destructive); border-color: var(--color-destructive); }
.warning { color: var(--color-warning); border-color: var(--color-warning); }
.success { color: var(--color-success); border-color: var(--color-success); }
.info { color: var(--color-info); border-color: var(--color-info); }

/* Variants */
.solid.danger { background: var(--color-destructive); color: var(--color-destructive-foreground); }
.soft.danger {
  /* oklch relative color syntax — check browser support (Chrome 119+, Safari 18+) */
  /* Fallback: use a pre-computed color or opacity on the element */
  background: oklch(from var(--color-destructive) l c h / 0.1);
}
.outline { background: transparent; }
```

## Rules
- Separate `variant` (visual) from `intent` (semantic) — two independent props.
- Use CVA `compoundVariants` (Tailwind) or CSS compound selectors (CSS Modules) for the matrix.
- All colors reference design tokens — never hardcode `red-600` or `#dc2626`.
- Include icon mapping per intent: danger=AlertCircle, warning=AlertTriangle, success=CheckCircle, info=Info.
- Extend for custom intents by adding new tokens + compound variant entries.
- Export `VariantProps` types from CVA for automatic TypeScript inference.
