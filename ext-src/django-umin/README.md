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
    path('crud/', include(registry.get_urls())),
]
```

### 4. Access your CRUD interface

Visit `/crud/book/` to see your CRUD interface!

**Note**: The library uses underscore-separated URL names (e.g., `book_list`, `book_create`, `book_update`, `book_delete`) instead of colon-separated names to avoid conflicts with Django's namespace system.

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
            return reverse('book_detail', kwargs={'pk': obj.pk})
        return super().get_success_url(obj)
```


## Template Tags

The library provides custom template tags for URL generation and field rendering.

### URL Generation

Use the `crud_url` tag instead of Django's `url` tag:

```html
{% load django_umin_tags %}

<!-- Correct usage -->
<a href="{% crud_url 'book' 'create' %}">Add Book</a>
<a href="{% crud_url 'book' 'update' book.pk %}">Edit Book</a>

<!-- Old usage (no longer supported) -->
<a href="{% url 'book:create' %}">Add Book</a>
```

### Field Rendering

Use the `get_attribute` filter to safely access object attributes:

```html
{% load django_umin_tags %}

{{ book|get_attribute:'title' }}
```

## Template Customization

### Override Individual Templates

Create templates in your app's template directory:

```
your_app/templates/django_umin/
├── base.html          # Base layout
├── list.html          # List view
├── list_htmx.html     # List view HTMX partial
├── form.html          # Create/Update form (full page)
├── form_htmx.html     # Create/Update form (HTMX partial)
└── delete.html        # Delete confirmation (full page)
└── delete_htmx.html   # Delete confirmation (HTMX partial)
```

### Example: Custom Base Template

```html
<!-- templates/django_umin/base.html -->
{% extends "django_umin/base.html" %}
{% load django_umin_tags %}

{% block nav_title %}
    My Custom App
{% endblock %}

{% block nav_items %}
    <a href="{% crud_url 'book' 'list' %}">Books</a>
    <a href="{% crud_url 'author' 'list' %}">Authors</a>
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

## Vite Development

Django UMIN includes built-in Vite integration for frontend development with hot module replacement (HMR).

### Development Server

Start the Vite dev server to watch all apps with frontend assets:

```bash
python manage.py vite_dev
```

This will automatically discover and watch all Django apps that have a `fe/` directory (e.g., `labzero/fe/`, `myapp/fe/`, etc.). Changes to CSS or JavaScript files in any app will trigger hot reloading.

**Watch specific apps only:**

```bash
python manage.py vite_dev --app labzero --app myapp
```

**Keep the Vite config file for inspection:**

```bash
python manage.py vite_dev --keep-vite-config
```

By default, the temporary Vite configuration file is deleted when the server stops. Use `--keep-vite-config` to preserve it for debugging or inspection purposes.

The dev server will:
- Watch all `fe/` directories in specified (or all) apps
- Enable hot module replacement (HMR)
- Serve assets at `http://localhost:5173`

### Building for Production

Build optimized assets for all apps:

```bash
python manage.py vite_build
```

This will:
- Discover all apps with `fe/` directories
- Build minified assets with Vite
- Generate manifest files for production
- Output to each app's `static/{app_name}/dist/` directory

### Frontend Asset Structure

Organize your frontend assets in each app:

```
myapp/
├── fe/
│   ├── css/
│   │   └── app.css      # Main CSS file
│   └── js/
│       ├── main.js      # Main JS entry
│       └── page/
│           └── page.js  # Page-specific JS
```

### Using Assets in Templates

Enable dev mode in settings:

```python
# settings.py
DJANGO_UMIN_VITE_DEV_MODE = True  # Development
DJANGO_UMIN_VITE_DEV_SERVER_HOST = "localhost"
DJANGO_UMIN_VITE_DEV_SERVER_PORT = 5173
```

Load assets in templates:

```html
{% load django_umin_vite %}

<!-- In development: loads from Vite dev server with HMR -->
<!-- In production: loads from built assets with cache busting -->
{% vite_asset "@vite/client" "" %}
{% vite_asset "css/app.css" "myapp" %}
{% vite_asset "js/main.js" "myapp" %}
```

### Proxied Environments (GitHub Codespaces, etc.)

When developing in environments like GitHub Codespaces where the Vite dev server runs behind a proxy, you need additional configuration to enable HMR and proper asset loading.

#### Automatic Codespaces Detection

Add this to your `settings.py`:

```python
import os

DJANGO_UMIN_VITE_DEV_MODE = True

# Automatically detect GitHub Codespaces
CODESPACE_NAME = os.environ.get('CODESPACE_NAME')
if CODESPACE_NAME:
    # Full dev server URL for Codespaces
    DJANGO_UMIN_VITE_DEV_SERVER_URL = f"https://{CODESPACE_NAME}-5173.app.github.dev"

    # HMR configuration for WebSocket connection
    DJANGO_UMIN_VITE_HMR_PROTOCOL = "wss"
    DJANGO_UMIN_VITE_HMR_HOST = f"{CODESPACE_NAME}-5173.app.github.dev"
    DJANGO_UMIN_VITE_HMR_PORT = 443
    DJANGO_UMIN_VITE_HMR_CLIENT_PORT = 443
else:
    # Local development settings
    DJANGO_UMIN_VITE_DEV_SERVER_HOST = "localhost"
    DJANGO_UMIN_VITE_DEV_SERVER_PORT = 5173
```

#### Manual Proxy Configuration

For other proxied environments:

```python
# Full base URL (overrides host/port/protocol)
DJANGO_UMIN_VITE_DEV_SERVER_URL = "https://your-proxy-url.example.com"

# Or use individual components
DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL = "https"  # default: "http"
DJANGO_UMIN_VITE_DEV_SERVER_HOST = "your-proxy-url.example.com"
DJANGO_UMIN_VITE_DEV_SERVER_PORT = 443

# HMR WebSocket configuration
DJANGO_UMIN_VITE_HMR_PROTOCOL = "wss"  # or "https"
DJANGO_UMIN_VITE_HMR_HOST = "your-proxy-url.example.com"
DJANGO_UMIN_VITE_HMR_PORT = 443
DJANGO_UMIN_VITE_HMR_CLIENT_PORT = 443
```

#### Configuration Priority

The settings are evaluated in this order:

1. **`DJANGO_UMIN_VITE_DEV_SERVER_URL`** - If set, this full URL is used for all asset requests
2. **`DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL` + HOST + PORT** - Otherwise, these are combined to form the URL
3. **Default** - Falls back to `http://localhost:5173`

#### Starting Vite Dev Server in Codespaces

When running in Codespaces or with tunnels:

```bash
# The vite_dev command automatically configures this
python manage.py vite_dev
```

The command automatically:
- Sets `host: '0.0.0.0'` in the Vite config, making the server accessible from proxies
- Configures CORS with `origin: '*'` to accept requests from any hostname
- Sets permissive `Access-Control-Allow-Origin` headers
- This prevents "Blocked request" errors when accessing through Cloudflare tunnels, ngrok, etc.

**No additional Django configuration needed** - the Vite dev server is configured to accept requests from any origin in development mode.

### Multi-App Development

The Vite dev server watches **all apps** with `fe/` directories simultaneously. This means:

- Changes in `labzero/fe/` trigger HMR
- Changes in `myapp/fe/` trigger HMR
- Changes in any other app's `fe/` directory trigger HMR

No need to restart the dev server when switching between apps!

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

### URL reverse errors

The library uses underscore-separated URL names (e.g., `book_list`, `book_create`) instead of colon-separated names. Use the `crud_url` template tag:

```html
{% load django_umin_tags %}
<a href="{% crud_url 'book' 'list' %}">Books</a>
```

### Template tag recursion errors

Make sure you're using `{% load django_umin_tags %}` and the correct filter names (`get_attribute` instead of `getattr`).

## Examples Repository

Check the `examples/` directory for complete working examples:

- Simple blog CRUD
- E-commerce product management
- Multi-tenant application

## Migration Guide

#### URL Name Changes

- **Old**: `book:list`, `book:create`, `book:update`, `book:delete`
- **New**: `book_list`, `book_create`, `book_update`, `book_delete`

#### Template Tag Changes

- **Old**: `{% url 'book:create' %}`
- **New**: `{% crud_url 'book' 'create' %}`

#### Template Filter Changes

- **Old**: `{{ obj|getattr:'field' }}`
- **New**: `{{ obj|get_attribute:'field' }}`

#### Template Updates

1. Add `{% load django_umin_tags %}` to all templates
2. Replace all `{% url %}` tags with `{% crud_url %}` tags
3. Replace all `{{ obj|getattr:field }}` with `{{ obj|get_attribute:field }}`

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
