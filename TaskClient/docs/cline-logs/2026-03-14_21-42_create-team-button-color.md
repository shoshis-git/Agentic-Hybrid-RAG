# שינוי צבע כפתור "צור צוות" לכחול־סגלגל

**תאריך ושעה:** 2026-03-14 21:42 (Asia/Jerusalem)

## מה השתנה
כפתור **"+ צור צוות"** בעמוד רשימת הצוותים עודכן לצבע כחול־סגלגל (gradient), במקום הטורקיז/סגול שהיה קודם.

## קבצים
- `src/app/features/teams/team-list/team-list.html` (לא שונה — זיהוי הכפתור)
- `src/app/features/teams/team-list/team-list.css` (עודכן)

## פירוט שינוי (CSS)
בתוך:
```css
.create-team-box button { ... }
```

שונה ה-gradient מ:
```css
background: linear-gradient(135deg, #06b6d4, #8b5cf6);
```
ל:
```css
background: linear-gradient(135deg, #6366f1, #8b5cf6);
```

## בדיקה
בוצע `npm run build` בהצלחה (עם אזהרות budget קיימות על גדלי CSS).
