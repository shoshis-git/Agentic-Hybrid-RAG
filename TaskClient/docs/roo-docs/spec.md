# TaskClient - Architecture Specification

**Written:** March 12, 2026 at 4:08 PM

## Project Overview
TaskClient is a task management SPA built with **Angular 21**. It is organized around the domains **auth**, **teams**, **projects**, **tasks**, and **comments**.

The app uses:
- **Standalone components** (no NgModules)
- **Angular Signals** for local reactive state
- **RxJS + HttpClient** for I/O
- **SSR + hydration** (Angular SSR + Express)

## Architecture Pattern

### High-Level Architecture
The application follows a **feature-based** structure with separation between:
- **Core Layer**: Shared services, guards, and interceptors
- **Features Layer**: Feature modules with their own components
- **Shared Layer**: Reusable components, directives, and models

```
src/app/
├── core/                    # Core business logic
│   ├── guards/             # Route guards (AuthGuard)
│   ├── interceptors/       # HTTP interceptors (auth-interceptor)
│   └── services/           # Business services
│       ├── auth/           # Authentication service
│       ├── task/           # Task management service
│       ├── project/        # Project management service
│       ├── team/           # Team management service
│       ├── user/           # User management service
│       └── comment/        # Comment service
├── features/               # Feature modules
│   ├── auth/              # Authentication (login, register)
│   ├── home/              # Landing page
│   ├── header/            # Navigation header
│   ├── footer/            # Footer component
│   ├── teams/             # Team management
│   ├── projects/          # Project management
│   ├── tasks/             # Task board (Kanban)
│   └── comments/          # Comments component
└── shared/                # Shared resources
    ├── modales.ts         # TypeScript interfaces/models
    └── directives/        # Custom directives
```

## Core Components

### 1. Application Bootstrap
- **Client entrypoint**: `src/main.ts` → `bootstrapApplication(App, appConfig)`
- **Root component**: `src/app/app.ts` (RouterOutlet + layout components)
- **Providers**: `src/app/app.config.ts`
  - router, HttpClient, interceptor, charts, hydration

### 2. SSR / Server entrypoints
- **SSR bootstrap**: `src/main.server.ts` → `bootstrapApplication(App, config, context)`
- **Server providers**: `src/app/app.config.server.ts` → `provideServerRendering(withRoutes(serverRoutes))`
- **Node server**: `src/server.ts`
  - Express 5 static hosting of `dist/.../browser`
  - Delegates non-static requests to `AngularNodeAppEngine`

### 3. Routing Architecture
The application uses Angular Router with the following route structure (`src/app/app.routes.ts`):

```typescript
/ (root)
├── /home              # Landing page (public)
├── /login             # Login page (public)
├── /register          # Registration page (public)
├── /teams             # Team list (protected)
├── /teams/:teamId/projects  # Project list for team (protected)
└── /tasks/:projectId  # Task board (protected)
```

**Route protection**: protected routes use `canActivate: [AuthGuard]`.

**Server routing**: `src/app/app.routes.server.ts` prerenders `**` (RenderMode.Prerender).

### 4. State Management

#### Signals-based reactivity
The application uses Angular Signals for reactive state:

- **[`AuthService.currentUser`](src/app/core/services/auth/auth.ts:17)**: Signal holding current authenticated user
- **[`TaskService.tasksSignal`](src/app/core/services/task/task-service.ts:16)**: Signal holding task list
- **Computed Signals**: 
  - [`todoTasks`](src/app/core/services/task/task-service.ts:19), [`inProgressTasks`](src/app/core/services/task/task-service.ts:20), [`doneTasks`](src/app/core/services/task/task-service.ts:21) - Filtered task lists by status
  - [`filtered`](src/app/features/tasks/task-board/task-board.ts:236) - Tasks filtered by current user

#### Persistence & session
- JWT token stored in `localStorage`
- Session validation on startup via `GET /auth/me`
- Token attached to requests via HTTP interceptor

### 5. HTTP Communication

#### API integration
- **Base URL**: `environment.apiUrl` (see `src/environments/environment*.ts`)
- **Auth**: `Authorization: Bearer <token>` header via `authInterceptor`
- **Services**: one service per domain in `src/app/core/services/*`

Note: `CommentService` and `ServiceProject` import `environment.development` directly (inconsistent with other services).

#### API Endpoints Structure
```
/api/auth/
  - POST /login
  - POST /register
  - GET /me

/api/teams/
  - GET /
  - POST /
  - DELETE /:teamId
  - POST /:teamId/members
  - DELETE /:teamId/members/:userId
  - GET /:teamId/members

/api/projects/
  - GET /
  - POST /
  - PATCH /:projectId
  - DELETE /:projectId

/api/tasks/
  - GET / (with projectId query param)
  - POST /
  - PATCH /:taskId
  - DELETE /:taskId
```

### 6. Authentication Flow

1. **Login/Register**: User submits credentials → [`AuthService`](src/app/core/services/auth/auth.ts:13) sends request
2. **Token Storage**: JWT token received and stored in localStorage
3. **User State**: User object stored in [`currentUser`](src/app/core/services/auth/auth.ts:17) signal
4. **Session Check**: On app init, [`checkSession()`](src/app/core/services/auth/auth.ts:23) validates token via `/auth/me` endpoint
5. **Request Interception**: [`authInterceptor`](src/app/core/interceptors/auth-interceptor.ts:4) adds Bearer token to all HTTP requests
6. **Route Protection**: [`AuthGuard`](src/app/core/guards/auth-guard.ts:10) prevents unauthorized access

### 7. Component Architecture

#### Standalone components
Components use `imports: [...]` in the component decorator instead of NgModules.

#### Component communication patterns observed
- Inputs: `input.required<T>()` (Angular v17+ input API) is used in `CommentsComponent`.
- Services: components call core services directly and manage local state via signals.
- (Potential coupling issue) `CommentsComponent` injects `TaskBoard` component to call `closeComments()`.

#### Key Components

**`TaskBoard`** (`src/app/features/tasks/task-board/task-board.ts`) - main task management interface
- Kanban board view (todo, in-progress, done)
- Task filtering (all vs assigned to current user)
- Task CRUD operations
- Member assignment
- Priority management
- Comments integration

**[`Header`](src/app/features/header/header.ts)** - Navigation component
- Conditional rendering based on authentication state
- User profile display
- Logout functionality

**[`CommentsComponent`](src/app/features/comments/comments.ts)** - Task comments
- Display comments for specific task
- Add new comments
- Real-time comment count updates

### 8. UI/UX Features

#### UI toolkit
- Angular Material + CDK
- Custom theme: `src/material-theme.scss`

#### User Feedback
- **SweetAlert2**: Modal dialogs for confirmations and notifications
- **Loading States**: [`isLoading`](src/app/features/tasks/task-board/task-board.ts:27) signals for async operations

#### Animations
- Scroll reveal directive using `IntersectionObserver` (`src/app/shared/directives/scroll-reveal.ts`)

#### Charts
- **ng2-charts**: Chart.js integration for data visualization

### 9. Data Models

Core TypeScript interfaces are defined in `src/app/shared/modales.ts`:

```typescript
- User: id, name, email, role
- Teams: id, name, created_at, members_count, members
- Projects: id, team_id, name, description, status, created_at
- Tasks: id, project_id, title, description, status, priority, assignee_id, due_date, order_index, timestamps
- Comments: id, task_id, user_id, body, created_at, author_name
```

### 10. Testing Strategy
- Test tooling: Vitest + JSDOM (see `package.json`)
- Unit tests exist as `.spec.ts` next to services/components

### 11. Build & Deployment

#### Development
```bash
npm start  # ng serve on localhost:4200
```

#### Production Build
```bash
npm run build  # Optimized production build
```

#### Server-Side Rendering (SSR)
- Angular SSR (`@angular/ssr`)
- Express server (`src/server.ts`)
- Hydration with event replay (`provideClientHydration(withEventReplay())`)

## Design Patterns (Observed)

### 1. Dependency Injection
- Constructor injection using `inject()` function
- Services provided at root level (`providedIn: 'root'`)

### 2. Observable Pattern
- RxJS for async operations
- `tap` operator for side effects (updating signals)
- Subscription management in components

### 3. Guard Pattern
- Functional guards using `CanActivateFn`
- Route protection based on authentication state

### 4. Interceptor Pattern
- Functional HTTP interceptors
- Automatic token attachment to requests

### 5. Signal Pattern
- Reactive state management with Angular Signals
- Computed values for derived state
- Automatic change detection

## Security Considerations (Client-side)

1. **JWT Authentication**: Token-based authentication with Bearer scheme
2. **Route Guards**: Protected routes require authentication
3. **HTTP Interceptor**: Automatic token attachment
4. **Token Validation**: Server-side validation via `/auth/me` endpoint
5. **Logout Mechanism**: Token removal and state cleanup

## Performance / UX Optimizations

1. **Standalone Components**: Better tree-shaking
2. **Signals**: Fine-grained reactivity, less change detection overhead
3. **Lazy Loading**: Feature-based code splitting potential
4. **SSR**: Server-side rendering for faster initial load
5. **Event Replay**: Hydration with event replay for better UX
6. **Production Build**: Minification, optimization, and hashing

## Scalability Considerations

1. **Feature-Based Structure**: Easy to add new features
2. **Service Layer**: Centralized business logic
3. **Shared Models**: Type safety across application
4. **Environment Configuration**: Easy deployment to different environments
5. **Modular Architecture**: Components can be extracted to libraries

## Open Questions / Things not inferable from this repo
- Database type, ORM, and server-side architecture are not present here (client-only repo). Any DB choice must be confirmed in the backend repository.
