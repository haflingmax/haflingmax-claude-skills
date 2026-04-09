# UI Component Quality & Design Consistency

## Component Completeness Standards

A component is NOT complete if it only renders markup. Every interactive component must
handle all states, expose a standard prop API, and satisfy WAI-ARIA requirements.

### Button (minimum)

- **States:** default, hover (`:hover`), focus-visible (`:focus-visible` with ring),
  active (`:active`), disabled (`disabled` + `aria-disabled="true"`),
  loading (disabled + spinner + text change like "Saving...")
- **Variants:** `default`, `destructive`, `outline`, `secondary`, `ghost`, `link`
- **Sizes:** `sm`, `default`, `lg`, `icon`
- **Props:** `variant`, `size`, `disabled`, `asChild`, `type`, `className`, `ref`
- **Accessibility:** keyboard activation (Space + Enter), `aria-label` when icon-only,
  `aria-pressed` for toggles

### Input (minimum)

- **States:** default, focus (visible ring), disabled, invalid (`aria-invalid="true"`),
  required (`required` attribute)
- **Props:** `type`, `disabled`, `required`, `placeholder`, `value`/`onChange`, `className`
- **Accessibility:** MUST have associated `<label>` via `htmlFor`/`id` (mandatory — not
  just placeholder). Error message linked via `aria-describedby`.
- **Type-specific:**
  - `email`: `inputMode="email"`, `autoComplete="email"`
  - `password`: show/hide toggle, `autoComplete="current-password"` or `"new-password"`
  - `number`: prefer `inputMode="numeric"` + `pattern="[0-9]*"` over `type="number"`
  - `tel`: `inputMode="tel"`, `autoComplete="tel"`

### Select/Dropdown (minimum)

- **States:** default, open, focus-visible, disabled, invalid
- **Keyboard:** Down/Up arrows navigate, Enter selects, Escape closes, type-ahead,
  Home/End for first/last
- **Accessibility:** `role="combobox"` on trigger, `aria-expanded`, `aria-controls`,
  `aria-activedescendant`, `aria-selected` on chosen option
- **Props:** `value`/`onValueChange`, `defaultValue`, `disabled`, `required`, `name`

### Dialog/Modal (minimum)

- **Accessibility:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` → title,
  `aria-describedby` → description
- **Keyboard:** Tab/Shift+Tab trapped (focus wrap), Escape closes
- **Focus:** moves into dialog on open, returns to trigger on close
- **Props:** `open`/`onOpenChange`, `modal`, compositional children (Trigger, Content,
  Title, Description, Close)

### Card (minimum)

- **Structure:** compositional — Card, CardHeader, CardTitle, CardDescription,
  CardContent, CardFooter
- **If interactive (clickable):** hover, focus-visible, active states; `role="button"`
  or wrapping `<a>`/`<button>`, `tabIndex="0"`, keyboard activation

---

## Design System Enforcement

### No Hardcoded Colors

Every color MUST reference a CSS custom property or Tailwind theme token.

<Good>
```tsx
<button className="bg-primary text-primary-foreground hover:bg-primary/90">
```
</Good>

<Bad>
```tsx
<button className="bg-[#3b82f6] text-white hover:bg-[#2563eb]">
```
</Bad>

### No Inline Styles

Zero `style={{}}` props except for truly dynamic computed values (e.g., percentage
widths from data). All static styling through Tailwind classes or CSS Modules.

### Spacing from Scale Only

Use Tailwind spacing scale (4px increments: 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24).
No arbitrary values like `p-[13px]` unless mathematically required.

Consistent spacing project-wide:
- Form field gap: one value (e.g., `gap-4` or `gap-6`)
- Section spacing: one value (e.g., `space-y-8`)
- Card padding: same for all cards

### Use `cn()` for Class Merging

All conditional/variant classes through `cn()` (clsx + tailwind-merge).
Never concatenate Tailwind class strings manually.

### Variants via CVA

Component variants MUST use `class-variance-authority` (cva) with explicit `variants`
and `defaultVariants`. Not ad-hoc ternaries in className.

```tsx
const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors ' +
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ' +
  'disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  }
)
```

---

## Component Extraction Rules

### When to Extract

Extract inline JSX to a shared component when:
1. The same pattern appears in **2+ places** (DRY)
2. The block exceeds **30 lines**
3. It contains its own **state management**
4. It matches an existing component in `components/ui/` but is reimplemented inline

### Single Source Rule

**One canonical version** of each component in `components/ui/`. No duplicate
Button/Input/Card implementations across the project. If a page has custom styling
for a base component, use `cn()` composition — not a new component file.

### ui/ Directory Structure

Every UI component with states/variants gets its own subfolder:

```
components/ui/
  button/
    Button.tsx           # Component with cva variants
    Button.test.tsx      # Tests: all states, keyboard, a11y
    Button.stories.tsx   # Storybook: all variants × sizes × states
    index.ts
  input/
    Input.tsx
    Input.test.tsx
    Input.stories.tsx
    index.ts
  select/
    Select.tsx           # Composed: Trigger + Content + Item
    Select.test.tsx
    Select.stories.tsx
    index.ts
```

Simple, stateless components (Separator, Badge without interaction) can stay as single files.

---

## Form UX Consistency

Every form in the project must follow the same pattern:

- Every input has a visible `<label>` (not just placeholder)
- Error messages below the field, linked via `aria-describedby`
- Required fields marked with `required` attribute AND visual indicator
- Disabled fields: `disabled` attribute + visual styling via `data-disabled`
- Submit button: loading state during submission, disabled while pending
- Consistent field gap project-wide (pick one: `gap-4` or `gap-6`)

### Field Pattern

```tsx
<div className="space-y-2">
  <label htmlFor="email" className="text-sm font-medium">
    Email <span className="text-destructive">*</span>
  </label>
  <input
    id="email"
    type="email"
    inputMode="email"
    autoComplete="email"
    required
    aria-invalid={!!error}
    aria-describedby={error ? 'email-error' : undefined}
    className={cn('...', error && 'border-destructive')}
  />
  {error && (
    <p id="email-error" role="alert" className="text-sm text-destructive">
      {error}
    </p>
  )}
</div>
```

---

## Review Checklist: UI Quality

When reviewing or auditing a project, flag these as **serious issues**:

- [ ] Components missing states (no hover, focus-visible, disabled, loading)
- [ ] Hardcoded colors (`bg-[#...]`, `text-[#...]`) instead of theme tokens
- [ ] Inline styles (`style={{}}`) for static values
- [ ] Arbitrary spacing (`p-[13px]`) instead of scale values
- [ ] Duplicated component implementations (2+ Buttons, 2+ Inputs)
- [ ] Inline JSX that duplicates an existing shared component
- [ ] Inputs without associated `<label>` elements
- [ ] No `aria-invalid` / `aria-describedby` on form fields with validation
- [ ] Missing keyboard navigation on custom interactive components
- [ ] No focus-visible ring on interactive elements
- [ ] Inconsistent spacing between form fields across pages
- [ ] Select/Dropdown without keyboard support (arrows, Escape, type-ahead)
- [ ] Dialog without focus trap or Escape-to-close
- [ ] No loading state on submit buttons
