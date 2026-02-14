# Quick Start

## Installation

Install django-umin using pip:

```bash
pip install django-umin
```

Or install from source:

```bash
git clone https://github.com/k4ml/django-umin.git
cd django-umin
pip install -e .
```

## Basic Setup

### 1. Add to INSTALLED_APPS

Add `django_umin` to your Django project's `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other apps
    'django_umin',
]
```

### 2. Configure Templates

Make sure your template settings include the app's templates:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        # ...
    },
]
```

### 3. Create a CRUD View

Create a CRUD view for your model:

```python
# myapp/crud_views.py
from django_umin.views import CRUDView
from .models import Book

class BookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author', 'published_date', 'isbn']
    list_display = ['title', 'author', 'published_date']
    search_fields = ['title', 'author']
```

### 4. Add URLs

Register the CRUD URLs:

```python
# myapp/urls.py
from django.urls import path, include
from .crud_views import BookCRUD

urlpatterns = [
    path('crud/', include(BookCRUD.get_urls())),
]
```

Or in your main `urls.py`:

```python
# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('myapp.urls')),
]
```

### 5. Access Your CRUD Interface

Run your development server:

```bash
python manage.py runserver
```

Navigate to:
- List view: `http://localhost:8000/books/crud/book/`
- Create: `http://localhost:8000/books/crud/book/create/`
- Update: `http://localhost:8000/books/crud/book/<id>/`
- Delete: `http://localhost:8000/books/crud/book/<id>/delete/`

## What's Next?

- Check out [Features](features.md) for advanced configuration
- Learn about [Bulk Actions](bulk-actions.md) for batch operations
- Explore the [API Reference](api.md) for detailed documentation
