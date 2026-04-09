# Design System Consistency & UX Rules

Complete reference for design tokens, styling rules, UX patterns, and anti-patterns.

---

## 1. Design Token Categories

Every project must define tokens (CSS custom properties or Tailwind theme) for:

| Category | Examples | Rule |
|----------|---------|------|
| **Color** | `--primary`, `--destructive`, `--muted` | Semantic + primitive. No raw hex in components. |
| **Typography** | `--font-sans`, `--text-sm`, `--text-base` | Scale with consistent ratio. |
| **Spacing** | 4px base: 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24 | No arbitrary values. |
| **Border radius** | `--radius-sm` (4px), `--radius-md` (8px), `--radius-lg` (16px), `--radius-full` | 4-5 discrete values. |
| **Shadow** | `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl` | 4-5 elevation levels. |
| **Z-index** | dropdown(1000), sticky(1100), overlay(1300), modal(1400), toast(1600) | Named scale, never raw numbers. |
| **Motion** | fast(100-150ms), normal(200-300ms), slow(400-500ms) | Duration + easing pairs. |
| **Breakpoints** | sm(640), md(768), lg(1024), xl(1280), 2xl(1536) | Mobile-first. |
| **Opacity** | disabled(0.5), hover-overlay(0.1), scrim(0.5) | Discrete values only. |

---

## 2. Color System

### Primitive vs Semantic

- **Primitives:** raw palette — `gray-50` through `gray-950`, never referenced in components
- **Semantic:** reference primitives — `--primary`, `--background`, `--foreground`, `--muted`

### Pairing Rule

Every background token has a designated foreground token:
- `--primary` / `--primary-foreground`
- `--destructive` / `--destructive-foreground`
- `--muted` / `--muted-foreground`

Never allow arbitrary fg/bg combinations.

### Contrast Ratios (WCAG 2.1 AA)

| Usage | Minimum ratio |
|-------|--------------|
| Normal text (< 18pt) | 4.5:1 |
| Large text (>= 18pt or >= 14pt bold) | 3:1 |
| UI components and graphics | 3:1 |
| Focus indicators | 3:1 against both background and component |
| Disabled / decorative | Exempt |

### Dark Mode

- Swap semantic values, not primitive names
- Dark backgrounds: gray-900/950, NOT pure black
- Surface layers: `gray-900 → gray-850 → gray-800` (lighter = higher elevation)
- Shadows less visible — use borders + surface color differentiation
- Same contrast ratios in both modes

---

## 3. Typography

### Scale (rem-based)

`xs`(0.75rem), `sm`(0.875rem), `base`(1rem), `lg`(1.125rem), `xl`(1.25rem),
`2xl`(1.5rem), `3xl`(1.875rem), `4xl`(2.25rem), `5xl`(3rem), `6xl`(3.75rem)

### Line Height

- Body text: 1.5 (WCAG SC 1.4.12 minimum)
- Headings: 1.1–1.3 (tighter as size increases)
- UI labels: 1.0–1.25

### Font Weight

- 400 (regular): body, descriptions
- 500 (medium): labels, navigation
- 600 (semibold): subheadings, buttons, table headers
- 700 (bold): headings, strong emphasis
- Max 3-4 weights per project

### Heading Hierarchy

- One `h1` per page. Never skip levels (no h1 → h3).
- Visual size may differ from semantic level — use className for visual, correct `h` tag for semantics.

### Max Line Length

60-80 characters (`max-width: 65ch`). Wider causes eye-tracking fatigue.

---

## 4. Spacing

**Base unit: 4px.** All values are multiples.

| Scale | Use |
|-------|-----|
| 1-3 (4-12px) | Component internal: icon-to-text gap, input padding |
| 4-6 (16-24px) | Between components: form field gap, card padding |
| 8-12 (32-48px) | Layout: between sections |
| 16-24 (64-96px) | Page: hero padding, major sections |

**Rules:**
- `gap` instead of margins between siblings (no collapse issues)
- Parent controls spacing; children don't set external margins
- One consistent form field gap project-wide (pick `gap-4` or `gap-6`)
- No arbitrary values (`p-[13px]`) — if you need it, the scale is wrong

---

## 5. Elevation / Shadow

| Level | Token | Usage |
|-------|-------|-------|
| 0 | none | Flat elements, inline cards |
| 1 | sm | Cards on hover, slight lift |
| 2 | md | Dropdowns, popovers, FAB |
| 3 | lg | Modals, dialogs, drawers |
| 4 | xl | Toasts, highest temporary UI |

Higher z-index = equal or higher shadow. Dark mode: reduce shadow, increase border emphasis.

---

## 6. Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| none | 0 | Table cells, full-bleed |
| sm | 4px | Inputs, small badges |
| md | 6-8px | Buttons, cards (default) |
| lg | 12-16px | Modals, prominent cards |
| full | 9999px | Pills, avatars, circles |

**Nesting rule:** `inner-radius = outer-radius - padding`. If padding >= outer-radius, inner = 0.

---

## 7. Z-index (Named Scale)

| Token | Value | Usage |
|-------|-------|-------|
| base | 0 | Default |
| dropdown | 1000 | Selects, autocomplete |
| sticky | 1100 | Sticky headers |
| overlay | 1300 | Backdrops/scrims |
| modal | 1400 | Dialogs |
| popover | 1500 | Tooltips over modals |
| toast | 1600 | Toast notifications |

Use `isolation: isolate` on layout sections to contain z-index scope.
**Never use raw z-index numbers in components.**

---

## 8. Motion / Animation

### Duration Scale

| Token | Value | Usage |
|-------|-------|-------|
| instant | 0ms | Color changes, toggles |
| fast | 100-150ms | Button hover, ripple |
| normal | 200-300ms | Expand/collapse, fade, slide |
| slow | 400-500ms | Page transitions |

### Easing

- `ease-out`: elements entering screen
- `ease-in`: elements leaving screen
- `ease-in-out`: elements moving between positions
- `linear`: only for progress bars

### Enter/Exit

- Enter: fade-in + scale from 95-98% (or slide from edge)
- Exit: fade-out + scale down. Exit duration = ~75% of enter (snappier)

### prefers-reduced-motion (MANDATORY)

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Not optional.** Hard accessibility requirement.

---

## 9. Responsive Design

### Mobile-first. Always.

Write base styles for mobile, add complexity with `min-width` queries.

### Component Breakpoint Behavior

| Component | Mobile | Desktop |
|-----------|--------|---------|
| Navigation | Hamburger + drawer | Full nav bar |
| Sidebar | Hidden / overlay | Persistent / collapsible |
| Grid | 1 column | 2-4 columns |
| Table | Card layout or horizontal scroll | Full table |
| Dialog | Full-screen (sheet) | Centered modal |
| Popover | Full-width | Positioned |
| Command | Full-screen | Dropdown |

### Touch Targets

Minimum 44×44px (WCAG 2.5.8 AAA) or 24×24px (AA minimum).
8px minimum between adjacent targets.

### Container Queries

Use `@container` for components appearing in varying-width contexts.
Media queries for page-level layout shifts.

---

## 10. Layout

- **Grid:** 12-column. Gap: 16px mobile, 24px tablet, 32px desktop.
- **Container max-width:** 1280px for most content. 768px for prose/articles.
- **Sidebar:** collapsed 48-64px, expanded 240-280px, never >320px.
- **Header:** 56-64px desktop, 48-56px mobile. Consistent across all pages.

---

## 11. Icons

- **Sizes:** 16px (inline sm), 20px (default), 24px (headings), 32px+ (features)
- **Alignment:** `inline-flex` + `align-items: center` + `gap`
- **Icon-only buttons:** `aria-label` + tooltip + 44px min touch target + focus ring
- **Consistency:** one icon library. Don't mix outlined and filled in same context.

---

## 12. UX Patterns — Mandatory Consistency

### Loading States

| Pattern | When |
|---------|------|
| **Skeleton** | Initial load, known layout (cards, tables, text) |
| **Spinner** | Actions with unpredictable duration. Show after 300ms delay. |
| **Progress bar** | File uploads, multi-step, known percentage |

Never mix skeletons and spinners for same content type within one app.

### Empty States (4 types — each needs its own template)

1. **No data yet (first-time):** illustration + explanation + CTA ("Create your first X")
2. **No results (filtered):** message + clear-filters CTA
3. **Error loading:** error message + retry button
4. **Intentionally empty:** light message, optional CTA

### Error Handling

| Type | When |
|------|------|
| **Field inline** | Form validation — red border + text below field |
| **Toast** | Background action failure (auto-save network error) |
| **Page banner** | Critical: auth failure, 500 errors |
| **Component inline** | Single widget fails, rest of page works |

Never `alert()`. Never silently swallow errors.

### Confirmation Patterns

**Always confirm:** delete, bulk actions, send/publish, unsaved changes, payments, permissions
**Never confirm:** navigation, non-destructive toggles, adding items
**Modal text:** name the specific item ("Delete project 'Alpha'?"), never generic "Are you sure?"

### Feedback

| Intent | Pattern | Dismiss |
|--------|---------|---------|
| Success | Green toast | Auto 3-5s |
| Warning | Amber toast/banner | Manual |
| Info | Blue toast | Auto 5s |
| Error | Red toast/banner | Manual required |

All feedback: `role="alert"` or `aria-live="polite"`.

### Navigation

- **Breadcrumbs:** pages deeper than 2 levels
- **Back buttons:** within flows (wizards, detail pages)
- **Tabs:** same-page switching (2-7 items), Arrow keys to switch
- **Sidebar:** app-level sections, active state marked, grouped if >7 items

### Data Display

- **Pagination:** tables, search results. Shareable URLs.
- **Infinite scroll:** feeds, logs. Preserve scroll on back-nav.
- **Load more:** cards, media grids.

### Search

- Debounce 200-300ms. Loading indicator. Preserve query in URL.
- "No results" with suggestions. Clear (×) button. Recent searches dropdown.

### Tables

- Sortable: click header, directional arrow, default sort indicated
- Filterable: controls above, active filters visible, clear-all
- Row selection: checkbox column, select-all, bulk action bar
- Pagination: below table, total count, rows-per-page
- Responsive: sticky first column + scroll, or cards below `md`

### Forms

- **Inline edit:** single-field in lists. Click → edit, Enter → save, Escape → cancel.
- **Modal edit:** few fields, don't leave context.
- **Page edit:** new records, many fields, dedicated route.
- **All forms:** visible label, required indicator, grouped fields, logical tab order,
  disabled submit during submission with spinner, success/error feedback.

---

## 13. Anti-Patterns — Detection

### Styling Anti-Patterns

- Arbitrary "magic number" values (margin-top: 13px, z-index: 99999)
- Mixing spacing systems
- Raw hex/rgb in components instead of tokens
- Inconsistent border-radius across similar components
- Overriding tokens with `!important`
- Inline `style={{}}` for static values
- Different button heights across the app
- Inconsistent focus ring styles

### Consistency Violations

- Multiple loading patterns for same content type
- Inconsistent empty states (some illustrations, some text-only)
- Mixed confirmation patterns (sometimes modal, sometimes none)
- Different date formats across the app
- Inconsistent capitalization (Title Case vs Sentence case)
- Mixed icon styles (outlined + filled, different libraries)

### Detection (grep/lint)

```bash
# Hardcoded hex colors outside token definitions
grep -rn '#[0-9a-fA-F]\{3,8\}' --include="*.tsx" --include="*.css"

# Arbitrary Tailwind values
grep -rn '\[#' --include="*.tsx"
grep -rn 'p-\[' --include="*.tsx"  # arbitrary padding

# Raw z-index
grep -rn 'z-index' --include="*.tsx" --include="*.css"

# Inline styles
grep -rn 'style={{' --include="*.tsx"

# Missing aria-label on buttons with only icon children
# (requires AST analysis — use eslint-plugin-jsx-a11y)
```
