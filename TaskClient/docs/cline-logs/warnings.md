# Dark Mode – Warnings / Sensitive Areas / Challenges Log

## Sensitive areas noticed (pre-implementation)
1. **Hard-coded colors in component CSS**
   - Example: `src/app/features/header/header.css` uses many hard-coded light-theme colors (`#f0f7ff`, `#1e1b4b`, `#4b5563`, etc.).
   - Risk: Dark Mode won’t fully apply unless these are refactored to CSS variables or overridden via a dark-theme selector.

2. **Global button gradient**
   - `src/styles.css` defines `.btn-primary` gradient with hard-coded blues.
   - Risk: In dark mode, this may still be acceptable, but it could clash with dark surfaces; may need a dark override.

3. **Theme scope choice impacts everything**
   - If we apply theme by setting an attribute/class on `<html>` it is easy to scope: `[data-theme="dark"] ...`
   - Risk: Some selectors might have higher specificity in component styles, requiring explicit overrides or variable refactors.

4. **Angular Material theme integration**
   - `src/material-theme.scss` configures Material system variables and sets `color-scheme: light`.
   - Risk: toggling only app CSS without aligning `color-scheme` can lead to inconsistent native controls / Material styling.

## Challenges expected
- Avoiding a large refactor: prefer introducing CSS variables and updating only key components first (Header + global background/text), then iterating.
- Preventing theme “flash” on load: ensure theme is applied as early as possible during bootstrap.

## Changes made while implementing Dark Mode
1. **Refactoring header colors**
   - Action: Converted key header colors to CSS variables (`--header-*`, `--btn-*`) and added a new toggle button.
   - Sensitive area: logo gradient remains hard-coded (looks OK in dark mode, but may need future tuning).

2. **Theme application mechanism**
   - Action: Theme is applied by setting `document.documentElement.dataset.theme` (on `<html>`).
   - Sensitive area: this relies on running in the browser; ThemeService guards localStorage access, but `document` access assumes client-side execution (currently called from `App` constructor).

3. **Material `color-scheme` switching**
   - Action: Added `html[data-theme="dark"] body { color-scheme: dark; }` while keeping default light.
   - Sensitive area: this does not generate a full Material dark palette; it only adjusts `color-scheme`. If Material components are used heavily, a full dark Material theme may be needed later.

4. **Global body colors**
   - Action: Set `body { background: var(--app-bg); color: var(--app-text); }` and defined light/dark token sets in `src/styles.css`.
   - Sensitive area: other feature-level component styles may still have hard-coded backgrounds/text and will need incremental variable refactors for full coverage.
