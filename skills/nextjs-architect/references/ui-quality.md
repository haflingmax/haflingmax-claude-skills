# UI Component Quality Standards

Complete reference for component states, accessibility, and anti-patterns.
Based on WAI-ARIA Authoring Practices 1.2, shadcn/ui, Radix UI, Material Design 3.

## Universal Rules for ALL Interactive Components

Every interactive element MUST have these states:
1. **Default** (rest)
2. **Hover** (`@media (hover: hover)` guard for touch devices)
3. **Focus-visible** (`:focus-visible` ring — NOT on click, only keyboard)
4. **Active/Pressed** (`:active`)
5. **Disabled** (prefer `aria-disabled="true"` over `disabled` for focusability)
6. **Loading** (where applicable — spinner + disabled)
7. **Error** (where applicable)

Universal anti-patterns:
- Removing focus outlines without replacing them
- Using `div`/`span` instead of semantic `button`/`a`
- Missing `aria-label` on icon-only buttons
- Not returning focus to trigger when closing overlays
- Using `pointer-events: none` for disabled (invisible to assistive tech)
- Not handling Escape key on overlays
- Auto-playing without `prefers-reduced-motion` check
- Tooltips on elements that can't receive keyboard focus

---

## Component Catalog

### Buttons

**States:** default, hover, focus-visible (ring), active, disabled (`aria-disabled`), loading (spinner + disabled + text change)
**Variants:** default, destructive, outline, secondary, ghost, link
**Sizes:** sm, default, lg, icon
**Keyboard:** Space + Enter activate
**ARIA:** implicit `role="button"`. Icon-only: `aria-label` required. Toggle: `aria-pressed`
**Props:** variant, size, disabled, asChild, type, className, ref
**Anti-patterns:** `<div onClick>` instead of `<button>`, no loading state, no focus-visible

### Inputs

**States:** default, focused (ring), filled, disabled, read-only, error (`aria-invalid`), valid, placeholder-shown, autofilled
**ARIA:** `aria-invalid`, `aria-describedby` → error/helper text, `aria-required`
**MUST have:** associated `<label>` via `htmlFor`/`id` — placeholder is NOT a label
**Type-specific requirements:**
- `email`: `inputMode="email"`, `autoComplete="email"`
- `password`: show/hide toggle, `autoComplete="current-password"` or `"new-password"`
- `number`: prefer `inputMode="numeric"` + `pattern="[0-9]*"` over `type="number"`
- `tel`: `inputMode="tel"`, `autoComplete="tel"`
- `search`: clear button (×), `role="searchbox"`
- `url`: `inputMode="url"`, `autoComplete="url"`
**Anti-patterns:** placeholder-as-label, no error state, no disabled styling, `type="number"` spinner issues

### Textarea

Same as Input plus: auto-resize behavior, character count linked via `aria-describedby`

### Select / Dropdown

**States:** default, open, focused, disabled, error, placeholder
**ARIA:** `role="listbox"`, `role="option"`, `aria-selected`, `aria-expanded` on trigger
**Keyboard:** Enter/Space to open, Arrow Up/Down navigate, Enter to select, Escape to close, type-ahead, Home/End
**Anti-patterns:** no keyboard support, custom select without ARIA, no type-ahead

### Combobox (Autocomplete)

**States:** open, closed, loading results, no results, selected, error
**ARIA:** `role="combobox"`, `aria-expanded`, `aria-autocomplete`, `aria-activedescendant`
**Keyboard:** type to filter, Arrow Up/Down navigate, Enter to select, Escape to close
**Note:** Most complex form input — prefer using a library (cmdk, Radix, downshift)

### Checkbox

**States:** checked, unchecked, indeterminate (`aria-checked="mixed"`), disabled, focused, error
**ARIA:** `role="checkbox"`, `aria-checked`
**Keyboard:** Space to toggle
**Anti-patterns:** no indeterminate state for "select all" with partial selection

### Radio Group

**ARIA:** `role="radiogroup"`, `role="radio"`, `aria-checked`
**Keyboard:** Arrow keys move selection within group, Tab enters/exits group as one stop
**Anti-patterns:** Tab between individual radios (should use arrows)

### Switch / Toggle

**ARIA:** `role="switch"`, `aria-checked`
**Keyboard:** Enter/Space to toggle
**Must have:** visible label (not just on/off text)
**Anti-patterns:** switch without visible label, no visual distinction between on/off

### Slider

**ARIA:** `role="slider"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-valuetext`
**Keyboard:** Arrow Left/Right (or Up/Down), Page Up/Down large step, Home/End min/max
**States:** value, dragging, disabled, range (dual thumb)

### Toggle / Toggle Group

**ARIA:** `aria-pressed` (single), `role="group"` (group)
**Keyboard:** Enter/Space, Arrow keys in group
**States:** pressed, not-pressed, disabled

---

### Tabs

**ARIA:** `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`, `aria-controls`/`aria-labelledby`
**Keyboard:** Arrow Left/Right (horizontal) or Up/Down (vertical), Home/End, Enter/Space to activate
**States:** selected, focused, disabled, loading (panel content)
**Anti-patterns:** using tabs for sequential steps (use stepper), missing tabpanel association

### Accordion

**ARIA:** button inside heading, `aria-expanded`, `aria-controls` → panel, panel `role="region"` + `aria-labelledby`
**Keyboard:** Enter/Space toggle, Arrow Up/Down between headers, Home/End
**States:** expanded, collapsed, disabled
**Must animate:** height transition on expand/collapse

### Navigation Menu

**ARIA:** `nav` with label, `aria-current` for active page
**Keyboard:** Arrow keys between items, Enter to follow, Escape to close submenus
**Submenus:** hover intent delay (200-300ms)
**Responsive:** hamburger + drawer below `md`, full nav at `md`+

### Breadcrumb

**ARIA:** `nav` with `aria-label="Breadcrumb"`, `ol` list, current: `aria-current="page"`
**Anti-patterns:** current page as a clickable link

### Pagination

**ARIA:** `nav` with `aria-label="pagination"`, current: `aria-current="page"`
**States:** current, disabled (prev/next at boundaries), loading

### Sidebar

**ARIA:** `nav` or `complementary` landmark, `aria-expanded` on collapse toggle
**Responsive:** overlay + backdrop on mobile, persistent/collapsible on desktop
**Keyboard:** Escape to close on mobile

---

### Dialog / Modal

**ARIA:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` → title, `aria-describedby`
**Keyboard:** focus trapped (Tab/Shift+Tab wrap), Escape closes
**Focus:** into dialog on open → back to trigger on close
**Responsive:** full-screen on mobile, centered on desktop
**Must animate:** fade + scale enter/exit

### Alert Dialog

Same as Dialog EXCEPT: Escape should NOT close — user must make explicit choice.
Tab cycles through action buttons only.

### Sheet (Side Panel)

Same ARIA as Dialog. Slide enter/exit animation. States: open, closed, side (top/right/bottom/left).

### Drawer

Same as Sheet but bottom-anchored with drag-to-dismiss. Drag handle: `role="button"`.
Mobile-specific: touch drag gesture.

### Popover

**ARIA:** `aria-haspopup`, `aria-expanded`, content `role="dialog"` if interactive
**Keyboard:** Enter/Space to open, Escape to close, focus trapped if modal
**Positioning:** auto-flip/shift when near viewport edge
**Responsive:** full-width on mobile

### Tooltip

**ARIA:** `role="tooltip"`, trigger gets `aria-describedby`
**Appears:** on hover + focus, delay 200-500ms. Dismissed on Escape.
**MUST NOT contain interactive content** — use Popover instead
**Anti-patterns:** links/buttons inside tooltip, tooltip on non-focusable element

### Hover Card

Trigger needs `aria-describedby`. Hover delay ~200ms open, ~300ms close grace area.
NOT keyboard triggered — use Popover if keyboard access needed.
**Anti-pattern:** critical content only in hover cards

---

### Dropdown Menu / Context Menu / Menubar

**ARIA:** `role="menu"`, `role="menuitem"`, `role="menuitemcheckbox"`, `role="menuitemradio"`, `aria-haspopup`, `aria-expanded`
**Keyboard:** Arrow Up/Down navigate, Enter/Space select, Escape close, Home/End, type-ahead
**Focus:** return to trigger on close
**Context Menu:** triggered by right-click or Shift+F10

### Command Palette (cmdk)

**ARIA:** `role="listbox"` or `role="combobox"`
**Keyboard:** Arrow Up/Down navigate, Enter select, Escape close, type to filter
**States:** open, empty results, loading, grouped sections
**Responsive:** full-screen on mobile

---

### Table / Data Table

**ARIA:** native `table`/`thead`/`tbody`/`th`/`td`. `th` needs `scope="col"|"row"`. Sortable: `aria-sort`
**Keyboard (DataTable):** Arrow keys for cell navigation, Enter for cell actions
**States:** sortable, sorted asc/desc, selected rows, loading (skeleton rows), empty, error
**Responsive:** horizontal scroll with sticky first column, or card layout below `md`
**Anti-patterns:** `div` with `display: table`, no sort indicators, no empty state

### Card

**Structure:** compositional — Card > CardHeader > CardTitle + CardDescription > CardContent > CardFooter
**If interactive:** hover, focus-visible, active; wrapping `<a>` or `<button>`, `tabIndex="0"`
**Anti-patterns:** multiple nested links creating "tab soup", no focus-visible when clickable

### Avatar

**ARIA:** decorative `alt=""` if name elsewhere; `alt="[Name]"` if standalone
**States:** loading, loaded, fallback (initials/icon), error (broken image)

### Badge

**ARIA:** status badge `aria-label`; decorative `aria-hidden="true"`
**Variants:** default, secondary, destructive, outline

### Calendar

**ARIA:** `role="grid"`, `role="gridcell"`, `aria-selected`, `aria-disabled`
**Keyboard:** Arrows for days, Page Up/Down months, Shift+Page year, Home/End week, Enter/Space select
**States:** selected, today, disabled, range-start, range-end, in-range, outside-month
**Note:** One of the most complex components — use a library (react-day-picker, Radix)

### Carousel

**ARIA:** `role="region"` + `aria-roledescription="carousel"`, slides `aria-roledescription="slide"`, `aria-label="N of M"`
**Must:** pause on hover/focus. Must have pause control if auto-playing.
**Anti-patterns:** auto-playing without pause, no slide indicators

---

### Alert

**ARIA:** `role="alert"` (assertive) or `role="status"` (polite)
**Variants:** info, success, warning, error/destructive
**Not dismissible** by default — use Alert Dialog for actions

### Toast / Sonner

**ARIA:** `role="status"`, `aria-live="polite"`, `aria-atomic="true"`
**Auto-dismiss:** 5-8s, pause on hover/focus
**Keyboard:** Tab to action, Escape to dismiss
**Must animate:** enter/exit transitions

### Progress

**ARIA:** `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
**Indeterminate:** omit `aria-valuenow`
**States:** determinate (0-100%), indeterminate, complete

### Skeleton

**ARIA:** `aria-busy="true"` on container, `aria-hidden="true"` on skeleton elements
**Animation:** shimmer/pulse
**Use for:** content with known layout (cards, tables, text blocks)

---

### Scroll Area

Custom scrollbars must remain keyboard-scrollable. Show on hover/scroll.

### Separator

`role="separator"` with `aria-orientation`. Decorative: `role="none"`.

### Resizable

Splitter: `role="separator"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`.
Keyboard: Arrow keys resize, Home/End min/max.

---

## Cross-Cutting Requirements

### Components Requiring Enter/Exit Animation
Dialog, Sheet, Drawer, Dropdown Menu, Context Menu, Popover, Hover Card, Tooltip, Toast,
Accordion, Collapsible, Alert Dialog, Navigation Menu submenus, Select dropdown,
Combobox dropdown, Command palette, Carousel slides.

### Components Requiring Responsive Adaptation
Sidebar (overlay mobile), Navigation Menu (hamburger), Dialog (full-screen mobile),
Sheet/Drawer (bottom sheet mobile), Table (scroll/cards), Popover (full-width mobile),
DatePicker (native input mobile), Command (full-screen mobile), Tooltip (hide on touch).

### Loading State by Component Type
- **Skeleton:** Card, Table rows, Avatar, Text blocks, Calendar, Charts
- **Spinner:** Buttons (inline), full-page, async actions. Show after 300ms delay.
- **Progress bar:** File uploads, multi-step forms, known-duration processes
- **`aria-busy="true"`:** on any container whose content is loading

### Error State by Component Type
- **Table:** empty state, fetch error, row-level errors
- **Image/Avatar:** broken image fallback
- **Combobox/Command:** search failure, no results
- **Calendar:** date range validation
- **Chart:** data fetch failure, empty data set
- **File upload:** size/type rejection, upload failure

### Composition Patterns
- **Compound components:** Accordion, Tabs, Radio Group, Menu, Select, Navigation Menu, Toggle Group
- **asChild / Slot:** render trigger as caller's element (Radix pattern)
- **Render props:** DataTable cell renderers, Combobox option rendering
