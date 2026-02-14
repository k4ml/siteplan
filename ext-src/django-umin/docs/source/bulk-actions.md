# Bulk Actions

Bulk actions allow users to select multiple items and perform batch operations on them.

## Overview

Bulk actions provide:
- ✅ Checkbox selection (individual + select all)
- ✅ Action dropdown menu
- ✅ Live counter showing selected items
- ✅ Confirmation modals for destructive actions
- ✅ Built-in actions (delete, export CSV)
- ✅ Easy framework for custom actions

## Enable Bulk Actions

```python
from django_umin.views import CRUDView
from django_umin.actions import delete_selected, export_csv

class BookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author', 'published_date']
    
    # Enable bulk actions
    actions = [delete_selected, export_csv]
    actions_on_top = True      # Show above table
    actions_on_bottom = False   # Hide below table
```

## Built-in Actions

### delete_selected

Bulk delete with confirmation modal:

```python
from django_umin.actions import delete_selected

class BookCRUD(CRUDView):
    model = Book
    actions = [delete_selected]
```

Features:
- Beautiful confirmation modal
- Lists all items to be deleted
- Shows count of selected items
- Safe "Cancel" option

### export_csv

Export selected items as CSV:

```python
from django_umin.actions import export_csv

class BookCRUD(CRUDView):
    model = Book
    actions = [export_csv]
```

Downloads a CSV file with all fields of selected items.

## Custom Actions

### Simple Function Action

Create a simple action function:

```python
from django.contrib import messages

def mark_as_published(crud_view, request, queryset):
    count = queryset.update(status='published')
    messages.success(request, f"Marked {count} items as published")
    return None  # Return to list view

mark_as_published.short_description = "Mark as published"

class BookCRUD(CRUDView):
    model = Book
    actions = [delete_selected, mark_as_published]
```

### Class-Based Action

For more complex actions, use the Action class:

```python
from django_umin.actions import Action
from django.contrib import messages

class ArchiveAction(Action):
    short_description = "Archive selected items"
    
    def __call__(self, crud_view, request, queryset):
        count = queryset.update(archived=True)
        messages.success(request, f"Archived {count} items")
        return None

class BookCRUD(CRUDView):
    model = Book
    actions = [delete_selected, ArchiveAction()]
```

### Action with Confirmation

Create an action with custom confirmation:

```python
from django_umin.actions import Action
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib import messages

class PublishAction(Action):
    short_description = "Publish selected items"
    
    def __call__(self, crud_view, request, queryset):
        # Check if confirmed
        if request.method == "POST" and request.POST.get("confirm") == "yes":
            count = queryset.update(status='published', published_at=timezone.now())
            messages.success(request, f"Published {count} items")
            return None
        
        # Show confirmation
        context = {
            "title": "Publish Items?",
            "message": f"Are you sure you want to publish {queryset.count()} items?",
            "queryset": queryset,
            "action": "publish_selected",
        }
        
        if request.headers.get("HX-Request"):
            # HTMX modal
            return HttpResponse(
                render_to_string("myapp/confirm_publish.html", context, request)
            )
        
        # Full page for non-HTMX
        return render(request, "myapp/confirm_publish_full.html", context)

class BookCRUD(CRUDView):
    model = Book
    actions = [PublishAction()]
```

### Action Returning File

Create an action that returns a downloadable file:

```python
import csv
from django.http import HttpResponse

def export_custom_csv(crud_view, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="books.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Author', 'Year'])
    
    for book in queryset:
        writer.writerow([
            book.title,
            book.author,
            book.published_date.year if book.published_date else ''
        ])
    
    return response

export_custom_csv.short_description = "Export as custom CSV"

class BookCRUD(CRUDView):
    model = Book
    actions = [export_custom_csv]
```

## Action Configuration

### Position

Control where actions appear:

```python
class BookCRUD(CRUDView):
    model = Book
    actions = [delete_selected, export_csv]
    actions_on_top = True       # Show above table
    actions_on_bottom = True    # Also show below table
```

### Disable Actions

Disable all actions:

```python
class BookCRUD(CRUDView):
    model = Book
    actions = []  # No bulk actions
```

### Conditional Actions

Dynamically determine available actions:

```python
class BookCRUD(CRUDView):
    model = Book
    
    def get_actions(self):
        actions = [export_csv]
        
        # Only staff can delete
        if self.request.user.is_staff:
            actions.append(delete_selected)
        
        return actions
```

## Action Function Signature

All actions must follow this signature:

```python
def my_action(crud_view, request, queryset):
    """
    Args:
        crud_view: The CRUDView instance
        request: HttpRequest object
        queryset: QuerySet of selected objects
    
    Returns:
        - None: Redirects back to list view
        - HttpResponse: Custom response (file download, redirect, etc.)
        - str: Rendered HTML (for confirmation pages)
    """
    pass

# Set description
my_action.short_description = "Action description"
```

## UI Components

The bulk actions interface includes:

1. **Checkbox column** - Select individual items
2. **Header checkbox** - Select/deselect all items on page
3. **Action dropdown** - Choose from available actions
4. **Go button** - Execute selected action (disabled when no items selected)
5. **Counter** - Shows "X items selected" (updates live with Alpine.js)
6. **Confirmation modals** - Beautiful modals for dangerous actions

## Screenshots

## Next Steps

- Explore more [Features](features.md)
- Check the [API Reference](api.md)
