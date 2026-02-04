# Bulk Actions Feature for django-umin

## Overview

Added a powerful **Bulk Actions** system to django-umin, similar to Django Admin's actions. This allows users to select multiple items and perform batch operations like delete, export, or custom actions.

## Features Added

### 1. Core Bulk Actions System (`actions.py`)

- **Action base class**: Framework for creating custom bulk actions
- **Built-in actions**:
  - `delete_selected`: Bulk delete with confirmation modal
  - `export_csv`: Export selected items as CSV

### 2. Updated Views (`views.py`)

- Added `actions` configuration to `CRUDView`
- Added `actions_on_top` and `actions_on_bottom` configuration
- Implemented POST handler in `CRUDListView` for action processing
- Action execution with confirmation support

### 3. Enhanced Templates

- **Checkbox selection** in list view (with select all)
- **Action dropdown** with "Go" button
- **Selected item counter** (live updating with Alpine.js)
- **Confirmation modals** for destructive actions
- **HTMX support** for seamless action execution

## Usage

### Basic Usage

```python
from django_umin.views import CRUDView
from django_umin.actions import delete_selected, export_csv

class BookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author', 'published_date', 'isbn']
    list_display = ['title', 'author', 'published_date']
    
    # Enable bulk actions
    actions = [delete_selected, export_csv]
    actions_on_top = True  # Show actions above the table
    actions_on_bottom = False  # Don't show actions below
```

### Custom Actions

Create your own bulk actions:

```python
from django_umin.actions import Action
from django.contrib import messages

class PublishSelectedAction(Action):
    short_description = "Publish selected items"
    
    def __call__(self, crud_view, request, queryset):
        # Update the selected items
        count = queryset.update(published=True)
        
        # Show success message
        messages.success(
            request, 
            f"Successfully published {count} items."
        )
        
        # Return None to go back to list view
        return None

# Or as a function
def publish_selected(crud_view, request, queryset):
    count = queryset.update(published=True)
    messages.success(request, f"Published {count} items.")
    return None

publish_selected.short_description = "Publish selected items"

# Use in your CRUD view
class ArticleCRUD(CRUDView):
    model = Article
    actions = [delete_selected, export_csv, publish_selected]
```

### Action Return Values

Actions can return:
- **None**: Redirects back to the list view
- **HttpResponse**: Custom response (e.g., file download, redirect)
- **String (HTML)**: Rendered template for confirmation pages

### Disabling Actions

```python
class BookCRUD(CRUDView):
    model = Book
    actions = []  # Disable all actions
```

### Default Actions

If `actions` is not specified, `delete_selected` is enabled by default:

```python
class BookCRUD(CRUDView):
    model = Book
    # actions defaults to [delete_selected]
```

## User Experience

1. **Select items**: Users can click checkboxes to select individual items or use the header checkbox to select all
2. **Choose action**: Select an action from the dropdown menu
3. **Execute**: Click "Go" button
4. **Confirm**: For destructive actions, a confirmation modal appears
5. **Complete**: Action executes and shows success message

## UI Features

- **Real-time counter**: Shows number of selected items
- **Select all**: Header checkbox selects/deselects all items on the page
- **Disabled state**: "Go" button is disabled when no items are selected
- **HTMX integration**: Actions work smoothly with HTMX for better UX
- **Mobile responsive**: Actions bar works on mobile devices

## Technical Details

### Action Function Signature

```python
def my_action(crud_view, request, queryset):
    """
    Args:
        crud_view: CRUDView instance
        request: HttpRequest object
        queryset: QuerySet of selected objects
    
    Returns:
        HttpResponse, str, or None
    """
    pass
```

### Confirmation Pattern

For actions that need confirmation:

```python
def dangerous_action(crud_view, request, queryset):
    if request.method == "POST" and request.POST.get("confirm") == "yes":
        # Actually perform the action
        queryset.delete()
        messages.success(request, "Deleted successfully")
        return None
    
    # Show confirmation page
    context = {
        "queryset": queryset,
        "count": queryset.count(),
        ...
    }
    
    if request.headers.get("HX-Request"):
        return render_to_string("my_confirm.html", context, request)
    
    # Full page for non-HTMX
    return render_to_string("my_confirm_full.html", context, request)
```

## Files Added/Modified

### New Files:
- `src/django_umin/actions.py` - Bulk actions framework
- `src/django_umin/templates/django_umin/actions/confirm_delete.html` - HTMX modal
- `src/django_umin/templates/django_umin/actions/confirm_delete_full.html` - Full page confirmation

### Modified Files:
- `src/django_umin/views.py` - Added action support to CRUDView and CRUDListView
- `src/django_umin/templates/django_umin/list_content.html` - Added checkboxes and action bar

## Testing

The feature is demonstrated in the test project:

```bash
cd django-umin-test
uv run python manage.py runserver
```

Visit http://localhost:8000/crud/book/ and try:
1. Select multiple books
2. Choose "Delete selected items" and confirm
3. Select books and choose "Export selected as CSV"

## Future Enhancements

Potential improvements:
- Permissions check per action
- Action groups/categories
- Async actions with progress bar
- Bulk edit form
- Action history/undo
- More built-in actions (duplicate, archive, etc.)

## Benefits Over Django Admin

- Modern UI with Tailwind CSS
- HTMX for smooth interactions
- Alpine.js for reactive UI
- Mobile-friendly design
- Easy to customize templates
- Lightweight and focused

This feature makes django-umin significantly more powerful for real-world CRUD applications! 🚀
