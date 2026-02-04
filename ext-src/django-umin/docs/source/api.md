# API Reference

## CRUDView

Main class for creating CRUD interfaces.

```python
from django_umin.views import CRUDView

class MyCRUD(CRUDView):
    model = MyModel
```

### Attributes

#### model
**Type:** `django.db.models.Model`  
**Required:** Yes

The Django model to create a CRUD interface for.

#### fields
**Type:** `list[str]` or `None`  
**Default:** `None`

List of field names to include in create/update forms.

```python
fields = ['title', 'author', 'published_date']
```

#### exclude
**Type:** `list[str]` or `None`  
**Default:** `None`

List of field names to exclude from forms.

#### list_display
**Type:** `list[str]`  
**Default:** `['__str__']`

Fields to display in the list view.

```python
list_display = ['title', 'author', 'published_date']
```

#### list_display_links
**Type:** `list[str]` or `None`  
**Default:** First field in `list_display`

Fields that should be clickable links to the detail/edit page.

#### search_fields
**Type:** `list[str]`  
**Default:** `[]`

Fields to search across.

```python
search_fields = ['title', 'author', 'isbn']
```

#### ordering
**Type:** `list[str]` or `None`  
**Default:** `None`

Default ordering for list view.

```python
ordering = ['-created_at', 'title']
```

#### paginate_by
**Type:** `int`  
**Default:** `10`

Number of items per page.

#### actions
**Type:** `list[callable]`  
**Default:** `[delete_selected]`

List of bulk actions available in list view.

```python
from django_umin.actions import delete_selected, export_csv

actions = [delete_selected, export_csv]
```

#### actions_on_top
**Type:** `bool`  
**Default:** `True`

Show action bar above the table.

#### actions_on_bottom
**Type:** `bool`  
**Default:** `False`

Show action bar below the table.

#### form_class
**Type:** `django.forms.ModelForm` or `None`  
**Default:** `None`

Custom form class for create/update views.

#### url_namespace
**Type:** `str`  
**Default:** Model name (lowercase)

Namespace for URL names.

#### login_required
**Type:** `bool`  
**Default:** `False`

Require authentication for all views.

### Methods

#### get_urls()
**Returns:** `list[URLPattern]`

Get URL patterns for this CRUD view.

```python
urlpatterns = [
    path('books/', include(BookCRUD.get_urls())),
]
```

#### get_queryset()
**Returns:** `QuerySet`

Get the base queryset. Override to filter or annotate.

```python
def get_queryset(self):
    qs = super().get_queryset()
    return qs.filter(author=self.request.user)
```

#### get_actions()
**Returns:** `list[tuple[str, str]]`

Get available actions as list of (name, description) tuples.

```python
def get_actions(self):
    actions = super().get_actions()
    if not self.request.user.is_staff:
        actions = [a for a in actions if a[0] != 'delete_selected']
    return actions
```

#### has_add_permission(request)
**Returns:** `bool`

Check if user can create objects.

```python
def has_add_permission(self, request):
    return request.user.is_staff
```

#### has_change_permission(request, obj=None)
**Returns:** `bool`

Check if user can edit objects.

#### has_delete_permission(request, obj=None)
**Returns:** `bool`

Check if user can delete objects.

## Actions

### delete_selected

Built-in action for bulk deletion with confirmation.

```python
from django_umin.actions import delete_selected

class BookCRUD(CRUDView):
    model = Book
    actions = [delete_selected]
```

### export_csv

Built-in action for exporting selected items as CSV.

```python
from django_umin.actions import export_csv

class BookCRUD(CRUDView):
    model = Book
    actions = [export_csv]
```

### Action Class

Base class for creating custom actions.

```python
from django_umin.actions import Action

class MyAction(Action):
    short_description = "My custom action"
    
    def __call__(self, crud_view, request, queryset):
        # Your logic here
        return None
```

#### Attributes

- **short_description** (`str`): Display name in dropdown
- **permission_required** (`str` or `None`): Optional permission check

#### Methods

**__call__(crud_view, request, queryset)**

Execute the action.

**Parameters:**
- `crud_view`: CRUDView instance
- `request`: HttpRequest object
- `queryset`: QuerySet of selected objects

**Returns:**
- `None`: Redirect to list view
- `HttpResponse`: Custom response
- `str`: Rendered HTML (for HTMX)

## Template Tags

### crud_url

Generate URLs for CRUD views.

```django
{% load django_umin_tags %}

<a href="{% crud_url 'book' 'list' %}">List</a>
<a href="{% crud_url 'book' 'create' %}">Create</a>
<a href="{% crud_url 'book' 'update' obj.pk %}">Edit</a>
<a href="{% crud_url 'book' 'delete' obj.pk %}">Delete</a>
```

### get_attribute

Get attribute value from object.

```django
{% load django_umin_tags %}

{{ obj|get_attribute:'field_name' }}
```

## Exceptions

### ImproperlyConfigured

Raised when CRUDView is not properly configured.

```python
from django.core.exceptions import ImproperlyConfigured

# Missing model
class BadCRUD(CRUDView):
    pass  # Raises ImproperlyConfigured
```
