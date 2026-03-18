# Task Edit Feature Implementation

**Written:** March 12, 2026 at 8:59 PM

## Overview
Added the ability to edit tasks similar to how projects can be edited. Users can now modify task details including title, description, priority, and due date through a modal dialog.

## Reason for Change
**Decision**: Add task editing capability to improve user experience (UX)

The edit feature was implemented to enhance the overall user experience by:
- **Reducing friction**: Users no longer need to delete and recreate tasks to fix mistakes or update details
- **Unified interface**: Provides a consistent editing pattern across the application (similar to project editing)
- **Improved productivity**: Users can quickly modify task information without leaving the task board view
- **Better data management**: Allows users to update task metadata (title, description, due date) that were previously immutable after creation
- **User control**: Empowers users to maintain accurate task information throughout the project lifecycle

## Changes Made

### 1. TaskService Enhancement (`src/app/core/services/task/task-service.ts`)
Updated the `updateTask()` method signature to support full task updates:

```typescript
updateTask(id: number, updates: { 
  status?: string; 
  priority?: string; 
  assignee_id?: number; 
  title?: string;           // NEW
  description?: string;     // NEW
  due_date?: Date           // NEW
}): Observable<Tasks>
```

**Purpose**: Allows the service to handle updates to task title, description, and due date in addition to existing status and priority updates.

### 2. TaskBoard Component (`src/app/features/tasks/task-board/task-board.ts`)
Added new `onEditTask()` method that:
- Opens a SweetAlert2 modal with editable fields
- Displays current task values in input fields
- Validates that the title is not empty
- Sends update request to the backend
- Updates the local task list on success
- Shows success/error notifications

**Method Signature**:
```typescript
onEditTask(task: Tasks): void
```

**Features**:
- Modal form with fields for:
  - Title (required)
  - Description (textarea)
  - Priority (dropdown: low, medium, high)
  - Due Date (date picker)
- Form validation (title is mandatory)
- Success toast notification
- Error handling with permission checks
- Automatic UI update after successful edit

### 3. Task Board Template (`src/app/features/tasks/task-board/task-board.html`)
Added edit buttons (✏️ עריכה) to all three task columns:

**Todo Column** (line 135):
```html
<button class="btn-edit" (click)="onEditTask(task)">✏️ עריכה</button>
```

**In Progress Column** (line 195):
```html
<button class="btn-edit" (click)="onEditTask(task)">✏️ עריכה</button>
```

**Done Column** (line 227):
```html
<button class="btn-edit" (click)="onEditTask(task)">✏️ עריכה</button>
```

## User Experience

### Before
Users could only:
- Change task status
- Change task priority
- Assign/reassign users
- Delete tasks
- Add comments

### After
Users can now also:
- Edit task title
- Edit task description
- Change priority through the edit modal
- Set/modify due dates
- All from a single unified edit dialog

## Implementation Pattern
The implementation follows the same pattern as the project edit feature:
1. Click edit button → Opens SweetAlert2 modal
2. Modal displays current values
3. User modifies fields
4. Form validates input
5. API call updates the resource
6. Local state updates
7. Success notification shown

## API Integration
The feature relies on the existing PATCH endpoint:
```
PATCH /api/tasks/{id}
```

The backend should accept the following fields:
- `title` (string, required)
- `description` (string, optional)
- `priority` (string: 'low' | 'medium' | 'high')
- `due_date` (date, optional)

## Error Handling
- **403 Forbidden**: Shows message "אין לך הרשאה לערוך משימה זו" (You don't have permission to edit this task)
- **Other Errors**: Shows generic "שגיאה בעדכון" (Update error) message

## Styling
Uses existing CSS classes:
- `.btn-edit`: Edit button styling
- `.swal2-input`: Input field styling
- `.swal2-textarea`: Textarea styling

## Testing Checklist
- [ ] Edit button appears on all task cards
- [ ] Modal opens with current task values
- [ ] Title field is required
- [ ] Priority dropdown shows correct current value
- [ ] Due date field displays correctly
- [ ] Form submission updates task
- [ ] Success notification appears
- [ ] Task list updates without page refresh
- [ ] Error handling works for permission denied
- [ ] Edit works across all task statuses (todo, in-progress, done)
