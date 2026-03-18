# Dark Mode Feature Plan

## Information gathered (from repo structure)
- Framework: Angular (presence of `angular.json`, `src/main.ts`, `src/app/app.config.ts`, routes).
- Global styling entry points:
  - `src/styles.css`
  - `src/material-theme.scss` (suggests Angular Material theming may be used).
- App shell / good UI insertion point:
  - `src/app/app.html`, `src/app/app.ts`
  - `src/app/features/header/header.*` (ideal place for a theme toggle control).
- SSR-related files exist (`src/main.server.ts`, `src/app/app.config.server.ts`), so theme application timing matters (avoid flash).

## Goals
1. Add a user-facing Dark Mode toggle.
2. Persist preference across refreshes.
3. Apply theme across the app with minimal invasive CSS changes.
4. Avoid breaking Angular Material theming (if present) and SSR.

## Plan (step-by-step)
### 1) Inspect current styling and theming (read-only)
- Read these files to choose the lowest-risk implementation:
  - `src/styles.css`
  - `src/material-theme.scss`
  - `src/app/app.html`, `src/app/app.ts`
  - `src/app/features/header/header.html`, `header.ts`, `header.css`
- Determine:
  - Are there existing CSS variables?
  - Are colors hard-coded widely?
  - Is Angular Material theme actually imported/applied?

### 2) Choose implementation approach
- Prefer **CSS variables** controlled by a root attribute:
  - Set `document.documentElement.dataset.theme = 'dark' | 'light'`
  - Write variables for light defaults and override them under `[data-theme="dark"]`
- If Angular Material theming is actively used, align the approach with `material-theme.scss`
  - Potentially toggle a class on the root for Material theme scoping.

### 3) Implement theme state + persistence
- Add `src/app/core/services/theme/theme.service.ts`
  - API: `getTheme()`, `setTheme(theme)`, `toggleTheme()`, `initTheme()`
  - Store preference in `localStorage` (e.g. key: `theme`)
  - On first load, default to `prefers-color-scheme` when no saved value.

### 4) Initialize theme early (reduce “flash”)
- Call `ThemeService.initTheme()` from the earliest safe bootstrap point (likely `app.ts` or an app initializer in config).
- If SSR renders initial HTML, consider a minimal inline script or server-provided attribute later if needed (only if flash is noticeable).

### 5) Add UI toggle
- Add a toggle button in `src/app/features/header/header.html`
- Wire to `ThemeService.toggleTheme()` in `header.ts`
- Style in `header.css` (ensure accessible contrast/focus states).

### 6) Add global theme variables
- Update `src/styles.css` (or import a dedicated theme file) with:
  - `:root { --bg: ...; --text: ...; --surface: ...; --border: ...; }`
  - `[data-theme="dark"] { ...dark overrides... }`
- Update a small number of existing global selectors to use the variables (incremental, not a full refactor).

### 7) Record sensitive areas during implementation
- While coding, record issues/sensitive areas in `.cursor-logs/warnings.md` (examples below):
  - Angular Material theme integration points
  - Hard-coded component colors that block dark mode
  - SSR/hydration causing theme flicker

### 8) Test/verify
- Run:
  - `npm test` (if configured) / `npm run lint` (if configured) / `npm run build`
  - `npm start` or `npm run dev` (depending on scripts)
- Manually verify key screens for contrast and readability.

## Dependent files likely to be edited/added
- Add:
  - `.cursor-logs/plan.md`
  - `.cursor-logs/warnings.md`
  - `src/app/core/services/theme/theme.service.ts`
- Edit (depending on inspection results):
  - `src/styles.css`
  - `src/material-theme.scss` (if Material is in use)
  - `src/app/app.ts` and/or `src/app/app.config.ts`
  - `src/app/features/header/header.*`

## Acceptance criteria
- Toggle switches theme instantly.
- Preference is persisted after refresh.
- No major layout regressions.
- No runtime errors in console.
