# django_umin/actions.py
"""
Bulk actions for django-umin CRUD views.
Similar to Django Admin's actions system.
"""
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string


class Action:
    """Base class for bulk actions."""

    # Action configuration
    short_description = None  # Display name for the action
    permission_required = None  # Optional permission required to use this action

    def __init__(self, short_description=None):
        if short_description:
            self.short_description = short_description

    def __call__(self, crud_view, request, queryset):
        """
        Execute the action.
        
        Args:
            crud_view: The CRUDView instance
            request: The HttpRequest object
            queryset: QuerySet of selected objects
        
        Returns:
            HttpResponse or None. If None, the list view will be shown.
        """
        raise NotImplementedError("Subclasses must implement __call__")


class DeleteSelectedAction(Action):
    """Default bulk delete action."""

    short_description = "Delete selected items"

    def __call__(self, crud_view, request, queryset):
        count = queryset.count()
        model_name = crud_view.model._meta.verbose_name_plural

        if request.method == "POST" and request.POST.get("confirm") == "yes":
            # Actually delete the objects
            queryset.delete()
            messages.success(
                request, f"Successfully deleted {count} {model_name}."
            )
            return None  # Return to list view

        # Show confirmation page
        context = {
            "action": "delete_selected",
            "queryset": queryset,
            "count": count,
            "model_name": model_name,
            "crud_view": crud_view,
            "url_namespace": crud_view.get_url_namespace(),
        }

        if request.headers.get("HX-Request"):
            html = render_to_string(
                "django_umin/actions/confirm_delete.html", context, request
            )
            return HttpResponse(html)

        # Return HttpResponse for non-HTMX requests too
        from django.shortcuts import render
        return render(request, "django_umin/actions/confirm_delete_full.html", context)


def delete_selected(crud_view, request, queryset):
    """Default delete selected action function."""
    action = DeleteSelectedAction()
    return action(crud_view, request, queryset)


delete_selected.short_description = "Delete selected items"


class ExportCSVAction(Action):
    """Export selected items as CSV."""

    short_description = "Export selected as CSV"

    def __call__(self, crud_view, request, queryset):
        import csv
        from django.http import HttpResponse

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{crud_view.model._meta.model_name}_export.csv"'
        )

        # Get fields to export (use list_display if available)
        fields = crud_view.list_display or [
            f.name
            for f in crud_view.model._meta.fields
            if not f.auto_created and f.editable
        ]

        writer = csv.writer(response)

        # Write header
        writer.writerow(fields)

        # Write data rows
        for obj in queryset:
            row = []
            for field in fields:
                if field == "__str__":
                    value = str(obj)
                else:
                    value = getattr(obj, field, "")
                row.append(value)
            writer.writerow(row)

        return response


def export_csv(crud_view, request, queryset):
    """Export selected items as CSV."""
    action = ExportCSVAction()
    return action(crud_view, request, queryset)


export_csv.short_description = "Export selected as CSV"
