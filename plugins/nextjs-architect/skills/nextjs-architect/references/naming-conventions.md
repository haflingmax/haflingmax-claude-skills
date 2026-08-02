# Naming Conventions

Consistent naming is mandatory. These rules apply project-wide.

---

## Files and Directories

| Type | Convention | Example |
|------|-----------|---------|
| Components | PascalCase | `ProductCard.tsx`, `AddToCartButton.tsx` |
| Hooks | camelCase, `use` prefix | `useDebounce.ts`, `useProductCard.ts` |
| Utilities | camelCase | `formatPrice.ts`, `cn.ts` |
| Types (standalone) | camelCase | `product.types.ts`, `api.types.ts` |
| Server Actions | kebab-case with `.action` | `add-to-cart.action.ts`, `contact.action.ts` |
| Tests | same name + `.test` | `ProductCard.test.tsx`, `useDebounce.test.ts` |
| Stories | same name + `.stories` | `ProductCard.stories.tsx` |
| Styles | same name + `.module.css` | `ProductCard.module.css` |
| Route segments | kebab-case | `app/product-detail/`, `app/user-settings/` |
| Route groups | lowercase in parens | `(auth)`, `(dashboard)`, `(marketing)` |
| Private folders | underscore prefix | `_components/`, `_hooks/`, `_lib/` |
| Directories | kebab-case | `components/add-to-cart/`, `features/user-profile/` |
| Constants files | camelCase | `constants.ts`, `config.ts` |

---

## Components

```tsx
// PascalCase for component name, matching file name
export function ProductCard({ product }: ProductCardProps) { ... }

// Props interface: ComponentName + Props
export interface ProductCardProps { ... }

// Default export ONLY for Next.js convention files (page, layout, error, etc.)
// Named exports everywhere else
```

---

## Event Handlers

| Where | Convention | Example |
|-------|-----------|---------|
| Implementation (inside component) | `handle` + Event | `handleClick`, `handleSubmit`, `handleInputChange` |
| Props (passed to component) | `on` + Event | `onClick`, `onSubmit`, `onChange` |

```tsx
// CORRECT
function ProductCard({ onAddToCart }: { onAddToCart: (id: string) => void }) {
  const handleClick = () => {
    onAddToCart(product.id)
  }
  return <button onClick={handleClick}>Add</button>
}

// WRONG — mixing handle/on
function ProductCard({ handleAddToCart }: ...) {  // ❌ Props use on*, not handle*
```

---

## Boolean Naming

Always prefix with `is`, `has`, `should`, `can`, `will`:

```tsx
// Props
interface ButtonProps {
  isLoading?: boolean     // ✅ not "loading"
  isDisabled?: boolean    // ✅ not "disabled" (for custom logic; native disabled is fine)
  hasError?: boolean      // ✅ not "error" (unless error is the Error object)
  shouldAutoFocus?: boolean
  canDelete?: boolean
}

// State
const [isOpen, setIsOpen] = useState(false)        // ✅ not "open"
const [isSubmitting, setIsSubmitting] = useState(false)
const [hasLoaded, setHasLoaded] = useState(false)
```

---

## Types and Interfaces

| Rule | Example |
|------|---------|
| **`interface`** for object shapes (props, API responses) | `interface ProductCardProps { ... }` |
| **`type`** for unions, intersections, computed types | `type ButtonVariant = 'primary' \| 'secondary'` |
| No `I` prefix (TypeScript team recommendation) | `ProductCardProps`, NOT `IProductCardProps` |
| `*Props` suffix for component props | `ButtonProps`, `DialogProps` |
| `*State` for state shapes | `CartState`, `AuthState` |
| `*Action` for action types | `CartAction`, `AddToCartAction` |
| `*Config` for configuration | `AppConfig`, `ThemeConfig` |
| `*Context` for React contexts | `AuthContext`, `ThemeContext` |

### Prefer `as const` objects over `enum`

```tsx
// PREFERRED — better tree-shaking, works with type inference
export const Status = {
  Pending: 'pending',
  Active: 'active',
  Inactive: 'inactive',
} as const

export type Status = (typeof Status)[keyof typeof Status]

// AVOID — enum
enum Status {       // ❌ Generates runtime JS, poor tree-shaking
  Pending = 'pending',
  Active = 'active',
}
```

---

## Constants

```tsx
// UPPER_SNAKE_CASE for true compile-time constants
export const MAX_RETRY_COUNT = 3
export const API_BASE_URL = 'https://api.example.com'
export const DEFAULT_PAGE_SIZE = 20

// camelCase for runtime-derived or computed values
export const defaultTheme = createTheme({ ... })
export const supportedLocales = ['en', 'ru', 'zh'] as const
```

---

## Server Actions

Verb-noun pattern with `Action` suffix:

```tsx
// features/cart/add-to-cart.action.ts
export async function addToCartAction(prevState: State, formData: FormData) { ... }

// features/product/update-product.action.ts
export async function updateProductAction(id: string, data: FormData) { ... }

// features/auth/login.action.ts
export async function loginAction(prevState: State, formData: FormData) { ... }
```

---

## Hooks

```tsx
// Always use* prefix. Name describes what the hook provides.
export function useProductCard(product: Product) { ... }   // returns view model
export function useDebounce<T>(value: T, delay: number) { ... }  // returns debounced value
export function useMediaQuery(query: string) { ... }       // returns boolean match

// Custom hook file: camelCase matching the function name
// useProductCard.ts, useDebounce.ts, useMediaQuery.ts
```

---

## CSS / Tailwind

| Approach | Convention |
|----------|-----------|
| CSS Modules | camelCase class names: `styles.cardWrapper`, not `styles['card-wrapper']` |
| Tailwind | Follow Tailwind's order: layout → sizing → spacing → typography → visual → states |
| CSS variables | kebab-case with prefix: `--color-primary`, `--spacing-md`, `--radius-lg` |
| Component variants | Use CVA with explicit variant names matching design system tokens |

---

## Anti-Patterns

- `MyComponent.jsx` → use `.tsx` always in TypeScript projects
- `IProps`, `IUser` → no Hungarian notation (`I` prefix)
- `enum` for string unions → use `as const` objects
- `data`, `info`, `item` as variable names → be specific (`product`, `userProfile`, `cartItem`)
- `handleOnClick` → redundant: use `handleClick` (implementation) or `onClick` (prop)
- `setIsOpenTrue` → use `setIsOpen(true)`, not a separate function
- `CONSTANTS.ts` exporting 50+ values → split by domain (`api.constants.ts`, `ui.constants.ts`)
- `utils.ts` as a junk drawer → split by function (`format.ts`, `validators.ts`, `cn.ts`)
