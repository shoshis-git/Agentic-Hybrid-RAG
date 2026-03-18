## Disable task editing (✏️) - 2026-03-14

### Goal
Remove the ability to *edit* a task via the ✏️ button (popup edit + save changes).

### Reason (Security)
This capability was removed for **security** reasons and to prevent users from changing **historical** task data after it was created.

### What was changed

#### UI: removed edit button + popup flow
- **File:** `src/app/features/tasks/task-board/task-board.html`
  - Removed the ✏️ **"עריכה"** button from all columns (todo / in-progress / done).

- **File:** `src/app/features/tasks/task-board/task-board.ts`
  - Removed `onEditTask(task: Tasks)` which previously opened a SweetAlert popup and called `TaskService.updateTask()` with title/description/priority/due_date.

#### Service-layer guard (client-side)
- **File:** `src/app/core/services/task/task-service.ts`
  - Added a guard inside `updateTask()` that blocks edits to **title / description / due_date**.
  - If any of those fields are provided, `updateTask()` now returns an Observable that errors immediately with a 400-like shape:
    ```ts
    { status: 400, error: { error: 'עריכת משימה (כותרת/תיאור/תאריך יעד) בוטלה בלקוח זה' } }
    ```
  - Status/priority/assignee updates are still allowed (used by board workflow).

#### Tests
- **File:** `src/app/core/services/task/task-service.spec.ts`
  - Added a unit test asserting `updateTask()` errors when trying to update the `title`.
  - Added `provideHttpClient()` to satisfy Angular DI for `HttpClient`.

### Notes / Verification
- Search confirmed there are no remaining references to `onEditTask` / `btn-edit` under `task-board`.
- After these changes, users can still:
  - create tasks
  - delete tasks
  - change status / priority
  - assign a user
  But cannot open or use an edit popup to change task details.

### Build / Test status
- `npm run build` ✅ succeeded.
- `npm test` ❌ currently fails due to **pre-existing** TypeScript issues not introduced by this change:
  - `src/app/core/services/auth/auth.spec.ts` imports `Auth` but the service is `AuthService`.
  - `src/app/core/services/team/team.spec.ts` imports `Team` but the service export differs.
  - `src/app/features/auth/login/register/register/register.ts` imports Node's `crypto` which is not available in the browser test build.
  - `src/app/features/comments/comments.spec.ts` is inconsistent (imports type `Comments` instead of `CommentsComponent`, duplicate imports).
