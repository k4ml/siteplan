# django_umin/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.admin.utils import flatten_fieldsets
from django.forms import modelform_factory
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator


class CRUDView:
    """
    Base CRUD view with Django admin-style API.

    Usage:
        class BookCRUD(CRUDView):
            model = Book
            fields = ['title', 'author', 'publisher', 'published_date']
            list_display = ['title', 'author', 'published_date']
            search_fields = ['title', 'author__name']
            list_filter = ['publisher', 'published_date']
            ordering = ['-published_date']
            paginate_by = 20
    """

    # Model configuration
    model = None

    # List view configuration
    list_display = None
    list_display_links = None
    search_fields = []
    list_filter = []
    ordering = None
    paginate_by = 25

    # Form configuration
    fields = None
    exclude = None
    fieldsets = None
    form_class = None

    # Template configuration
    template_name_suffix = None
    list_template = 'django_umin/list.html'
    form_template = 'django_umin/form.html'
    delete_template = 'django_umin/delete.html'

    # HTMX configuration
    htmx_template_suffix = '_htmx'

    # Permissions
    permission_required = None

    # Messages
    success_message_create = "{object} was created successfully."
    success_message_update = "{object} was updated successfully."
    success_message_delete = "{object} was deleted successfully."

    def __init__(self):
        if not self.model:
            raise ValueError("CRUDView requires 'model' to be set")

        if self.list_display is None:
            self.list_display = ['__str__']

        if self.list_display_links is None:
            self.list_display_links = [self.list_display[0]]

    def get_queryset(self, request):
        """Get base queryset with search and filtering applied."""
        queryset = self.model.objects.all()

        # Apply ordering
        if self.ordering:
            queryset = queryset.order_by(*self.ordering)

        # Apply search
        search_query = request.GET.get('q', '')
        if search_query and self.search_fields:
            from django.db.models import Q
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(query)

        # Apply filters
        for filter_field in self.list_filter:
            filter_value = request.GET.get(filter_field)
            if filter_value:
                queryset = queryset.filter(**{filter_field: filter_value})

        return queryset

    def get_form_class(self):
        """Get form class using admin-style configuration."""
        if self.form_class:
            return self.form_class

        fields = self.fields
        if self.fieldsets:
            fields = flatten_fieldsets(self.fieldsets)

        return modelform_factory(
            self.model,
            fields=fields,
            exclude=self.exclude
        )

    def get_template_name(self, base_template, request):
        """Get template name with HTMX support."""
        if request.headers.get('HX-Request'):
            # Return partial template for HTMX requests
            return base_template.replace('.html', f'{self.htmx_template_suffix}.html')
        return base_template

    def get_success_url(self, obj=None):
        """Get URL to redirect to after successful form submission."""
        return reverse(f'{self.get_url_namespace()}_list')

    def get_url_namespace(self):
        """Get URL namespace for this CRUD."""
        return self.model._meta.model_name

    def format_message(self, template, obj):
        """Format success message with object."""
        return template.format(object=str(obj))


class CRUDListView(ListView):
    """List view for CRUD operations."""

    crud_view = None

    def __init__(self, crud_view, **kwargs):
        super().__init__(**kwargs)
        self.crud_view = crud_view

    def get_queryset(self):
        return self.crud_view.get_queryset(self.request)

    def get_template_names(self):
        return [self.crud_view.get_template_name(self.crud_view.list_template, self.request)]

    def get_paginate_by(self, queryset):
        return self.crud_view.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'crud_view': self.crud_view,
            'model_name': self.crud_view.model._meta.verbose_name,
            'model_name_plural': self.crud_view.model._meta.verbose_name_plural,
            'search_query': self.request.GET.get('q', ''),
            'list_display': self.crud_view.list_display,
            'list_display_links': self.crud_view.list_display_links,
            'has_add_permission': True,  # Add permission checking here
            'url_namespace': self.crud_view.get_url_namespace(),
        })
        return context


class CRUDCreateView(CreateView):
    """Create view for CRUD operations."""

    crud_view = None

    def __init__(self, crud_view, **kwargs):
        super().__init__(**kwargs)
        self.crud_view = crud_view

    def get_form_class(self):
        return self.crud_view.get_form_class()

    def get_template_names(self):
        return [self.crud_view.get_template_name(self.crud_view.form_template, self.request)]

    def get_success_url(self):
        return self.crud_view.get_success_url(self.object)

    def form_valid(self, form):
        response = super().form_valid(form)
        msg = self.crud_view.format_message(
            self.crud_view.success_message_create,
            self.object
        )
        messages.success(self.request, msg)

        # For HTMX requests, return a redirect trigger
        if self.request.headers.get('HX-Request'):
            response['HX-Redirect'] = self.get_success_url()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'crud_view': self.crud_view,
            'model_name': self.crud_view.model._meta.verbose_name,
            'action': 'Create',
            'url_namespace': self.crud_view.get_url_namespace(),
        })
        return context


class CRUDUpdateView(UpdateView):
    """Update view for CRUD operations."""

    crud_view = None

    def __init__(self, crud_view, **kwargs):
        super().__init__(**kwargs)
        self.crud_view = crud_view

    def get_queryset(self):
        return self.crud_view.model.objects.all()

    def get_form_class(self):
        return self.crud_view.get_form_class()

    def get_template_names(self):
        return [self.crud_view.get_template_name(self.crud_view.form_template, self.request)]

    def get_success_url(self):
        return self.crud_view.get_success_url(self.object)

    def form_valid(self, form):
        response = super().form_valid(form)
        msg = self.crud_view.format_message(
            self.crud_view.success_message_update,
            self.object
        )
        messages.success(self.request, msg)

        if self.request.headers.get('HX-Request'):
            response['HX-Redirect'] = self.get_success_url()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'crud_view': self.crud_view,
            'model_name': self.crud_view.model._meta.verbose_name,
            'action': 'Update',
            'url_namespace': self.crud_view.get_url_namespace(),
        })
        return context


class CRUDDeleteView(DeleteView):
    """Delete view for CRUD operations."""

    crud_view = None

    def __init__(self, crud_view, **kwargs):
        super().__init__(**kwargs)
        self.crud_view = crud_view

    def get_queryset(self):
        return self.crud_view.model.objects.all()

    def get_template_names(self):
        return [self.crud_view.get_template_name(self.crud_view.delete_template, self.request)]

    def get_success_url(self):
        return self.crud_view.get_success_url()

    def form_valid(self, form):
        obj = self.get_object()
        msg = self.crud_view.format_message(
            self.crud_view.success_message_delete,
            obj
        )
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            # For HTMX requests, return the updated list content instead of redirecting
            # This ensures the UI updates immediately and the success message is shown
            from django.template.loader import render_to_string
            from django.contrib import messages

            messages.success(self.request, msg)

            # Get the updated queryset
            queryset = self.crud_view.get_queryset(self.request)

            # Render the list content with messages
            context = {
                'object_list': queryset,
                'crud_view': self.crud_view,
                'model_name': self.crud_view.model._meta.verbose_name,
                'model_name_plural': self.crud_view.model._meta.verbose_name_plural,
                'search_query': self.request.GET.get('q', ''),
                'list_display': self.crud_view.list_display,
                'list_display_links': self.crud_view.list_display_links,
                'has_add_permission': True,
                'url_namespace': self.crud_view.get_url_namespace(),
                'messages': list(messages.get_messages(self.request)),
            }

            # Check if pagination is needed
            paginate_by = self.crud_view.paginate_by
            if paginate_by:
                paginator = Paginator(queryset, paginate_by)
                page_number = self.request.GET.get('page', 1)
                page_obj = paginator.get_page(page_number)
                context.update({
                    'page_obj': page_obj,
                    'paginator': paginator,
                    'is_paginated': True,
                })
            else:
                context['is_paginated'] = False

            # Render the list content
            html = render_to_string('django_umin/list_htmx.html', context, self.request)

            # Return the HTML content with HX-Trigger for messages
            response = HttpResponse(html)
            response['HX-Trigger'] = 'showMessage'
            response['HX-Trigger-After-Swap'] = 'showMessage'

            return response

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'crud_view': self.crud_view,
            'model_name': self.crud_view.model._meta.verbose_name,
            'url_namespace': self.crud_view.get_url_namespace(),
        })
        return context
