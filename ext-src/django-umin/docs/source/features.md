# Features

## List Display

Control which fields are displayed in the list view:

```python
class BookCRUD(CRUDView):
    model = Book
    list_display = ['title', 'author', 'published_date']
    list_display_links = ['title']  # Clickable fields
```

## Search

Add search functionality to your CRUD view:

```python
class BookCRUD(CRUDView):
    model = Book
    search_fields = ['title', 'author', 'isbn']
```

Users can search across all specified fields using the search bar.

## Pagination

Control pagination settings:

```python
class BookCRUD(CRUDView):
    model = Book
    paginate_by = 25  # Items per page (default: 10)
```

## Field Configuration

Specify which fields to include in forms:

```python
class BookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author', 'published_date', 'isbn']
    # Or exclude specific fields:
    # exclude = ['created_at', 'updated_at']
```

## Permissions

Control access to CRUD operations:

```python
class BookCRUD(CRUDView):
    model = Book
    
    # Require authentication
    login_required = True
    
    # Or override per-operation
    def has_add_permission(self, request):
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
```

## Custom Form

Use a custom form class:

```python
from django import forms

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BookCRUD(CRUDView):
    model = Book
    form_class = BookForm
```

## URL Namespace

Customize the URL namespace:

```python
class BookCRUD(CRUDView):
    model = Book
    url_namespace = 'library'  # Default: model name
```

Then in templates:
```python
{% crud_url 'library' 'list' %}
```

## Template Customization

Override default templates:

```python
class BookCRUD(CRUDView):
    model = Book
    list_template_name = 'myapp/book_list.html'
    form_template_name = 'myapp/book_form.html'
    delete_template_name = 'myapp/book_confirm_delete.html'
```

## Ordering

Set default ordering:

```python
class BookCRUD(CRUDView):
    model = Book
    ordering = ['-published_date', 'title']
```

## Custom Queryset

Filter or annotate the queryset:

```python
class BookCRUD(CRUDView):
    model = Book
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Only show published books
        return qs.filter(status='published')
```

## Success Messages

Customize success messages:

```python
class BookCRUD(CRUDView):
    model = Book
    success_message_create = "Book added successfully!"
    success_message_update = "Book updated successfully!"
    success_message_delete = "Book deleted successfully!"
```

## Model Name Display

Customize model name display:

```python
class BookCRUD(CRUDView):
    model = Book
    
    def get_model_name(self):
        return "Library Book"
    
    def get_model_name_plural(self):
        return "Library Books"
```

## Next Steps

- Learn about [Bulk Actions](bulk-actions.md) for batch operations
- Check the [API Reference](api.md) for complete documentation
