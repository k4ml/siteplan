# 🎯 Quick Start: Bulk Actions

## What You Get

✅ **Select multiple items** with checkboxes
✅ **Delete in bulk** with beautiful confirmation modal
✅ **Export to CSV** with one click
✅ **Create custom actions** easily

## 30-Second Setup

```python
# books/crud_views.py
from django_umin.views import CRUDView
from django_umin.actions import delete_selected, export_csv

class BookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author', 'published_date', 'isbn']
    
    # That's it! Just add these two lines:
    actions = [delete_selected, export_csv]
    actions_on_top = True
```

## How It Works

### 1. User Sees
```
┌─────────────────────────────────────────────────┐
│ [Action ▼] [Go]              3 items selected   │
├─────────────────────────────────────────────────┤
│ [✓] | Title           | Author    | Date        │
│ [✓] | The Great Gatsby| Fitzgerald| 1925-04-10  │
│ [✓] | 1984            | Orwell    | 1949-06-08  │
│ [ ] | To Kill...      | Lee       | 1960-07-11  │
└─────────────────────────────────────────────────┘
```

### 2. User Selects Action
```
Action dropdown:
  - Delete selected items  ← Click
  - Export selected as CSV
```

### 3. Confirmation Modal Appears
```
┌───────────────────────────────┐
│    🚨 Delete 2 books?         │
│                               │
│  • The Great Gatsby           │
│  • 1984                       │
│                               │
│  [Cancel]  [Delete 2 Items]   │
└───────────────────────────────┘
```

### 4. Success!
```
✅ Successfully deleted 2 books.
```

## Custom Actions (Advanced)

### Quick Custom Action

```python
def mark_as_featured(crud_view, request, queryset):
    count = queryset.update(featured=True)
    messages.success(request, f"Marked {count} items as featured")

mark_as_featured.short_description = "Mark as featured"

class BookCRUD(CRUDView):
    model = Book
    actions = [delete_selected, export_csv, mark_as_featured]
```

### Custom Action with Confirmation

```python
from django_umin.actions import Action

class ArchiveAction(Action):
    short_description = "Archive selected items"
    
    def __call__(self, crud_view, request, queryset):
        if request.method == "POST" and request.POST.get("confirm"):
            count = queryset.update(archived=True)
            messages.success(request, f"Archived {count} items")
            return None  # Go back to list
        
        # Show confirmation
        context = {
            "title": "Archive Items?",
            "message": f"Archive {queryset.count()} items?",
            "queryset": queryset,
        }
        return render_to_string("my_confirm.html", context, request)
```

## Test It Now!

1. Open: http://100.120.76.71:7000/crud/book/
2. Click checkboxes to select books
3. Choose action from dropdown
4. Click "Go"
5. Confirm (if needed)

## What's Different From Django Admin?

| Feature | Django Admin | django-umin |
|---------|--------------|-------------|
| UI | Old, clunky | Modern, Tailwind |
| Mobile | ❌ Poor | ✅ Responsive |
| HTMX | ❌ Full reload | ✅ Smooth, no reload |
| Setup | Complex | Simple |
| Customization | Hard | Easy |

## Tips

💡 **Disable actions**: `actions = []`

💡 **Actions on bottom**: 
```python
actions_on_top = False
actions_on_bottom = True
```

💡 **Return CSV download**:
```python
def export_action(crud_view, request, queryset):
    response = HttpResponse(content_type='text/csv')
    # ... create CSV ...
    return response  # Returns file, doesn't redirect
```

💡 **Check permissions**:
```python
def delete_action(crud_view, request, queryset):
    if not request.user.has_perm('app.delete_model'):
        messages.error(request, "No permission")
        return None
    # ... do delete ...
```

---

That's it! Your CRUD interface now has professional bulk operations! 🚀
