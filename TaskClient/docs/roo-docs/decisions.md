# TaskClient - Technology Decisions

**Written:** March 12, 2026 at 8:49 PM

This document captures technology choices that are *observable in the codebase* (not assumptions about the backend implementation).

## Runtime / Framework

### Angular 21 (Standalone Components)
- Evidence: `@angular/core` `^21.1.0` and `@angular/cli` `^21.1.1` in `package.json`.
- Architecture choice: standalone APIs instead of NgModules.
  - Evidence: components declare `imports: [...]` in `@Component(...)` metadata (e.g. `src/app/app.ts`, `src/app/features/tasks/task-board/task-board.ts`).

### SSR + Hydration
- Server-side rendering is enabled with `@angular/ssr`.
  - Evidence: `@angular/ssr` dependency and Express SSR server in `src/server.ts`.
- Client hydration is enabled.
  - Evidence: `provideClientHydration(withEventReplay())` in `src/app/app.config.ts`.
- Server render mode includes prerendering.
  - Evidence: `RenderMode.Prerender` in `src/app/app.routes.server.ts`.

## Backend communication

### HTTP Client + REST API
- Uses Angular `HttpClient` across services.
  - Evidence: core services under `src/app/core/services/**`.
- REST style endpoints under a common base URL (`environment.apiUrl`).
  - Evidence: `src/environments/environment*.ts`.

### Environment-based configuration
- API base URL is controlled via Angular environments.
  - Evidence: `environment.apiUrl`.
- Note (inconsistency): some services import `environment.development` directly instead of `environment`.
  - Evidence: `ServiceProject` and `CommentService`.
  - Implication: production builds might still point at the development env file for those services.

## Authentication / Authorization (Client-side)

### ⚠️ CRITICAL: Auth Service File (`src/app/core/services/auth/auth.ts`)
- **This file is HIGHLY SENSITIVE and must be treated as a non-negotiable constraint.**
- **Rule: Any modifications to this file must be carefully reviewed and justified.**
- **Implication: Changes to auth logic, token handling, or session management require extreme caution.**

### JWT token in localStorage
- Stores an access token in `localStorage` under the `token` key.
  - Evidence: `src/app/core/services/auth/auth.ts`.
- Authenticated state is derived from token existence and a `/auth/me` request.
  - Evidence: `checkSession()` calling `GET /auth/me`.

### HTTP Interceptor adds Bearer token
- Uses functional interceptor `HttpInterceptorFn`.
  - Evidence: `src/app/core/interceptors/auth-interceptor.ts`.

### Route protection
- Uses a functional `CanActivateFn` guard.
  - Evidence: `src/app/core/guards/auth-guard.ts`.
- Protected routes: teams/projects/tasks routes require auth.
  - Evidence: `canActivate: [AuthGuard]` in `src/app/app.routes.ts`.

## State management

### Angular Signals for local state
- Uses `signal(...)` for component/service state and `computed(...)` for derived views.
  - Evidence: `AuthService.currentUser`, `TaskService.tasksSignal`, `TaskBoard` filtering signals.
- Decision: no external state library detected (no NgRx/Akita/etc in `package.json`).

### RxJS Observables for IO
- HTTP calls return `Observable<T>`; components subscribe.
  - Evidence: `TaskService.getTasks()`, `AuthService.login()` etc.
- `tap()` is used for side-effects (e.g. syncing server results into signals).
  - Evidence: `TaskService.getTasks()` and `AuthService.login()/register()`.

## UI / UX Libraries

### Angular Material + CDK
- Uses `@angular/material` and `@angular/cdk`.
  - Evidence: dependencies in `package.json` and theme file `src/material-theme.scss`.

### SweetAlert2 for dialogs/notifications
- Uses `sweetalert2`.
  - Evidence: imports `import Swal from 'sweetalert2';` in multiple feature components.

### Charts: Chart.js via ng2-charts
- Uses `chart.js` + `ng2-charts` and registers default chart elements.
  - Evidence: deps in `package.json`; `provideCharts(withDefaultRegisterables())` in `src/app/app.config.ts`.

## Testing

### Vitest + JSDOM
- Uses `vitest` and `jsdom`.
  - Evidence: `devDependencies` in `package.json`.
- `.spec.ts` tests exist for services/components.
  - Evidence: files under `src/app/**/**.spec.ts`.

## Styling

### Global styles + SCSS theme
- Global CSS: `src/styles.css`.
- Material theme in SCSS: `src/material-theme.scss`.
  - Evidence: both registered in `angular.json` build options.

## Deployment / Hosting (observable)

### Frontend API target is hosted on Render
- The API URL points to `onrender.com`.
  - Evidence: `https://task-project-azk0.onrender.com/api` in `environment*.ts`.

## Notable implementation choices / tradeoffs

- **Functional providers**: uses `provideHttpClient(withInterceptors([...]))` vs module-based `HttpClientModule`.
- **Functional routing**: uses `provideRouter(routes)`.
- **Potential duplication**: `provideRouter(routes)` appears twice in `app.config.ts`.
- **Potential DI issue**: `CommentsComponent` injects `TaskBoard` (a component) instead of a service.
  - Evidence: `private taskService = inject(TaskBoard)` in `src/app/features/comments/comments.ts`.
  - Implication: tighter coupling and may fail depending on component hierarchy / injector.
