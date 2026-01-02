# Django HTMX CRUD Library

A lightweight, modern Django library for creating CRUD interfaces using Django Admin-style API with HTMX and Tailwind CSS.

## Features

✨ **Django Admin-Style API** - Familiar configuration using `list_display`, `search_fields`, `list_filter`, etc.

⚡ **HTMX Integration** - Smooth, dynamic interactions without page reloads

🎨 **Modern Design** - Beautiful Tailwind CSS templates out of the box

🔧 **Highly Customizable** - Override templates, forms, and behavior easily

📱 **Responsive** - Mobile-friendly interface

🚀 **Minimal Setup** - Get CRUD working in minutes

## Installation

### 1. Install the package

```bash
pip install django-umin
```

### 2. Add to your Django project

Copy the `django_umin` directory to your Django project or install as a package.

### 3. Update settings.py

```python
INSTALLED_APPS = [
    # ... other apps
    'django_umin',
    'django.contrib.messages',  # Required for success messages
]

MIDDLEWARE = [
    # ... other middleware
    'django.contrib.messages.middleware.MessageMiddleware',
]
```

### 4. Create templates directory

Create `templates/django_umin/` directory in your project or ensure `APP_DIRS` is True in your `TEMPLATES` setting.

## Quick Start

### 1. Define your model

```python
# models.py
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13)
    
    def __str__(self):
        return self.title
```

### 2. Create a CRUD view

```python
# django_umin_views.py
from django_umin.views import CRUDView
from .models import Book

class BookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author', 'published_date', 'isbn']
    list_display = ['title', 'author', 'published_date']
    search_fields = ['title', 'author']
```

### 3. Register URLs

```python
from django_umin.urls import registry
from .crud_views import BookCRUD, AuthorCRUD

registry.register(BookCRUD)
registry.register(AuthorCRUD)

urlpatterns = [
    path('library/', include(registry.get_urls())),
]
```

### 4. Access your CRUD interface

Visit `/book/` to see your CRUD interface!

## Configuration Options

### List View Options

```python
class BookCRUD(CRUDView):
    model = Book
    
    # Display configuration
    list_display = ['title', 'author', 'published_date', 'status']
    list_display_links = ['title']  # Clickable fields (default: first field)
    
    # Search and filtering
    search_fields = ['title', 'author', 'isbn']
    list_filter = ['publisher', 'language', 'status']
    
    # Ordering and pagination
    ordering = ['-published_date']
    paginate_by = 25  # Items per page
```

### Form Configuration

```python
class BookCRUD(CRUDView):
    model = Book
    
    # Simple field list
    fields = ['title', 'author', 'publisher', 'isbn']
    
    # Or exclude fields
    exclude = ['created_at', 'updated_at']
    
    # Or use fieldsets (like admin)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author')
        }),
        ('Publishing Details', {
            'fields': ('publisher', 'isbn', 'published_date')
        }),
    )
    
    # Custom form class
    form_class = CustomBookForm
```

### Template Customization

```python
class BookCRUD(CRUDView):
    model = Book
    
    # Override default templates
    list_template = 'myapp/custom_list.html'
    form_template = 'myapp/custom_form.html'
    delete_template = 'myapp/custom_delete.html'
```

### Success Messages

```python
class BookCRUD(CRUDView):
    model = Book
    
    success_message_create = "Book '{object}' was added successfully!"
    success_message_update = "Book '{object}' was updated."
    success_message_delete = "Book '{object}' was deleted."
```

### Custom Behavior

```python
class BookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author']
    
    def get_queryset(self, request):
        """Customize queryset (e.g., filter by user)"""
        queryset = super().get_queryset(request)
        
        if not request.user.is_staff:
            queryset = queryset.filter(published=True)
        
        return queryset.select_related('publisher')
    
    def get_success_url(self, obj=None):
        """Customize redirect after form submission"""
        if obj:
            return reverse('book:detail', kwargs={'pk': obj.pk})
        return super().get_success_url(obj)
```


## Template Customization

### Override Individual Templates

Create templates in your app's template directory:

```
your_app/templates/django_umin/
├── base.html          # Base layout
├── list.html          # List view
├── list_htmx.html     # List view HTMX partial
├── form.html          # Create/Update form
└── delete.html        # Delete confirmation
```

### Example: Custom Base Template

```html
<!-- templates/django_umin/base.html -->
{% extends "django_umin/base.html" %}

{% block nav_title %}
    My Custom App
{% endblock %}

{% block nav_items %}
    <a href="{% url 'book:list' %}">Books</a>
    <a href="{% url 'author:list' %}">Authors</a>
{% endblock %}

{% block extra_head %}
    <style>
        /* Your custom styles */
    </style>
{% endblock %}
```

## Advanced Usage

### With Permissions

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from crud.views import CRUDView

class BookCRUD(LoginRequiredMixin, CRUDView):
    model = Book
    fields = ['title', 'author']
    login_url = '/login/'
```

### Custom Form Validation

```python
from django import forms

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
    
    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if len(isbn) != 13:
            raise forms.ValidationError("ISBN must be 13 digits")
        return isbn

class BookCRUD(CRUDView):
    model = Book
    form_class = BookForm
```

### Multiple CRUD Views for Same Model

```python
class PublicBookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author']
    list_display = ['title', 'author']
    
    def get_queryset(self, request):
        return Book.objects.filter(published=True)

class AdminBookCRUD(LoginRequiredMixin, CRUDView):
    model = Book
    fields = '__all__'
    list_display = ['title', 'author', 'status', 'created_at']
```

## HTMX Features

The library uses HTMX for:

- **Live Search** - Results update as you type (with debouncing)
- **Pagination** - Navigate pages without full reload
- **Delete Confirmation** - Modal appears via HTMX
- **Form Submission** - Smooth form handling

All HTMX features work automatically. For full page requests (non-HTMX), the library falls back to standard Django behavior.

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled for HTMX features
- Graceful degradation when JavaScript is disabled

## Dependencies

- Django 3.2+
- No additional Python packages required
- HTMX and Tailwind CSS loaded from CDN (can be customized)

## Customization Guide

### Changing the Design

The default templates use Tailwind CSS from CDN. To use custom CSS:

1. Override `base.html`
2. Replace the Tailwind CDN link with your own CSS
3. Update component classes as needed

### Adding Custom Actions

```python
# In your template
{% block extra_list_actions %}
    <button onclick="exportData()">Export CSV</button>
{% endblock %}
```

### Custom Field Rendering

Create a custom form template and use Django's form rendering:

```html
{% for field in form %}
    {% if field.name == 'special_field' %}
        <!-- Custom rendering -->
    {% else %}
        {{ field }}
    {% endif %}
{% endfor %}
```

## Performance Tips

1. **Use select_related/prefetch_related** in `get_queryset()`
2. **Index search fields** in your database
3. **Adjust pagination** with `paginate_by`
4. **Cache querysets** for read-heavy views

## Troubleshooting

### Templates not found

Ensure `APP_DIRS = True` in your `TEMPLATES` setting or add the django_umin app directory to `DIRS`.

### HTMX not working

Check that the HTMX script is loading from CDN. Open browser console for errors.

### Forms not submitting

Ensure `{% csrf_token %}` is present in your forms and Django's CSRF middleware is enabled.

### Custom templates not applying

Make sure your app is listed before `django_umin` in `INSTALLED_APPS` to override templates.

## Examples Repository

Check the `examples/` directory for complete working examples:

- Simple blog CRUD
- E-commerce product management
- Multi-tenant application

## Contributing

Contributions welcome! Please submit pull requests or open issues on GitHub.

## License

MIT License - see LICENSE file for details.

## Credits

Built with:
- Django
- HTMX
- Tailwind CSS
- Alpine.js (for UI interactions)

---

Made with ❤️ by the Django community
