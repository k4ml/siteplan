# django-umin Documentation

**Modern Django CRUD with HTMX**

django-umin is a lightweight Django library that provides beautiful, modern CRUD interfaces using HTMX and Tailwind CSS.

```{toctree}
:maxdepth: 2
:caption: Contents

quickstart
features
bulk-actions
api
contributing
```

## Features

- 🎨 **Modern UI** - Beautiful Tailwind CSS design
- ⚡ **HTMX Integration** - Smooth interactions without page reloads
- 📦 **Bulk Actions** - Select and process multiple items
- 🔍 **Search & Filters** - Built-in search functionality
- 📱 **Responsive** - Mobile-friendly design
- 🚀 **Easy Setup** - Minimal configuration required

## Quick Example

```python
from django_umin.views import CRUDView
from django_umin.actions import delete_selected, export_csv

class BookCRUD(CRUDView):
    model = Book
    fields = ['title', 'author', 'published_date', 'isbn']
    list_display = ['title', 'author', 'published_date']
    search_fields = ['title', 'author']
    
    # Enable bulk actions
    actions = [delete_selected, export_csv]
    actions_on_top = True
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
