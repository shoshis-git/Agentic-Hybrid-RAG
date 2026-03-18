# Dark Mode - Implementation TODO

- [x] Add ThemeService (`src/app/core/services/theme/theme.service.ts`)
  - [x] Persist `light|dark` in `localStorage` (default light)
  - [x] Apply via `document.documentElement.dataset.theme`
  - [x] Provide `init()`, `toggle()`, `setTheme()`, `isDark()`


- [x] Initialize theme early in app startup
  - [x] Update `src/app/app.ts` to call `themeService.init()`


- [x] Add UI toggle in header
  - [x] Update `src/app/features/header/header.html` (toggle button)
  - [x] Update `src/app/features/header/header.ts` (hook to ThemeService)
  - [x] Update `src/app/features/header/header.css` (style for toggle)


- [x] Global theming styles
  - [x] Update `src/styles.css` to define base CSS variables + dark overrides
  - [x] Update `src/material-theme.scss` to switch `color-scheme` based on `[data-theme='dark']`


- [x] Update `.cursor-logs/warnings.md` with any new sensitive areas found while editing


- [x] Run checks
  - [x] `npm run build` (and/or lint/test if configured)
