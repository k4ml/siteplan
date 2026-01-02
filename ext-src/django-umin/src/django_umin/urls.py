# crud/urls.py
from django.urls import path
from .views import CRUDListView, CRUDCreateView, CRUDUpdateView, CRUDDeleteView


class CRUDRegistry:
    """Registry for managing CRUD views with automatic URL generation."""

    def __init__(self):
        self._registry = {}

    def register(self, crud_view_class):
        """
        Register a CRUD view class.

        Usage:
            registry = CRUDRegistry()

            @registry.register
            class BookCRUD(CRUDView):
                model = Book
                fields = ['title', 'author']
        """
        crud_instance = crud_view_class()
        model_name = crud_instance.model._meta.model_name
        self._registry[model_name] = crud_instance
        return crud_view_class

    def get_urls(self):
        """Generate URL patterns for all registered CRUD views."""
        urlpatterns = []

        for model_name, crud_view in self._registry.items():
            patterns = self._generate_urls(crud_view)
            urlpatterns.extend(patterns)

        return urlpatterns

    def _generate_urls(self, crud_view):
        """Generate URL patterns for a single CRUD view."""
        model_name = crud_view.model._meta.model_name

        return [
            path(
                f'{model_name}/',
                CRUDListView.as_view(crud_view=crud_view),
                name=f'{model_name}_list'
            ),
            path(
                f'{model_name}/create/',
                CRUDCreateView.as_view(crud_view=crud_view),
                name=f'{model_name}_create'
            ),
            path(
                f'{model_name}/<int:pk>/',
                CRUDUpdateView.as_view(crud_view=crud_view),
                name=f'{model_name}_update'
            ),
            path(
                f'{model_name}/<int:pk>/delete/',
                CRUDDeleteView.as_view(crud_view=crud_view),
                name=f'{model_name}_delete'
            ),
        ]

    def get_crud(self, model_name):
        """Get CRUD view instance for a model."""
        return self._registry.get(model_name)


# Global registry instance
registry = CRUDRegistry()


# Alternative: Manual URL generation helper
def crud_urls(crud_view_class, prefix=''):
    """
    Generate URL patterns for a CRUD view.

    Usage:
        # In your urls.py
        from crud.urls import crud_urls
        from .crud_views import BookCRUD

        urlpatterns = [
            *crud_urls(BookCRUD, prefix='library/'),
        ]
    """
    crud_view = crud_view_class()
    model_name = crud_view.model._meta.model_name

    return [
        path(
            f'{prefix}{model_name}/',
            CRUDListView.as_view(crud_view=crud_view),
            name=f'{model_name}:list'
        ),
        path(
            f'{prefix}{model_name}/create/',
            CRUDCreateView.as_view(crud_view=crud_view),
            name=f'{model_name}:create'
        ),
        path(
            f'{prefix}{model_name}/<int:pk>/',
            CRUDUpdateView.as_view(crud_view=crud_view),
            name=f'{model_name}:update'
        ),
        path(
            f'{prefix}{model_name}/<int:pk>/delete/',
            CRUDDeleteView.as_view(crud_view=crud_view),
            name=f'{model_name}:delete'
        ),
    ]
