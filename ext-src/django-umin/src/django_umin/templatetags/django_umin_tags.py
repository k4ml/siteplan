# crud/templatetags/crud_tags.py
from django import template

register = template.Library()


@register.filter
def get_attribute(obj, attr):
    """Get attribute from object."""
    if obj is None:
        return ""

    if attr == "__str__":
        return str(obj)

    # Use Python's built-in getattr function directly
    import builtins

    try:
        return builtins.getattr(obj, attr)
    except (AttributeError, TypeError):
        return ""


@register.filter
def add(value, arg):
    """Add the arg to the value."""
    try:
        return value + arg
    except (ValueError, TypeError):
        try:
            return str(value) + str(arg)
        except (ValueError, TypeError):
            return ""


@register.simple_tag
def crud_url(url_namespace, action, pk=None):
    """Generate CRUD URL."""
    from django.urls import reverse

    url_name = f"{url_namespace}_{action}"

    # Use reverse with current_app=None to avoid namespace issues
    if pk:
        return reverse(url_name, kwargs={"pk": pk}, current_app=None)

    return reverse(url_name, current_app=None)


@register.inclusion_tag("crud/components/field.html")
def render_field(field, field_classes=""):
    """Render a form field with proper styling."""
    return {
        "field": field,
        "field_classes": field_classes,
    }


@register.inclusion_tag("crud/components/table_header.html")
def render_table_header(field, sortable=False, current_sort=""):
    """Render a table header with optional sorting."""
    return {
        "field": field,
        "sortable": sortable,
        "current_sort": current_sort,
    }


@register.filter
def verbose_name(model):
    """Get verbose name of a model."""
    return model._meta.verbose_name


@register.filter
def verbose_name_plural(model):
    """Get verbose name plural of a model."""
    return model._meta.verbose_name_plural


@register.simple_tag
def get_field_display(obj, field):
    """Get display value for a field, handling special cases."""
    if field == "__str__":
        return str(obj)

    try:
        value = getattr(obj, field)

        # Check for get_FOO_display method (for choices)
        display_method = f"get_{field}_display"
        if hasattr(obj, display_method):
            return getattr(obj, display_method)()

        # Handle callables
        if callable(value):
            return value()

        # Handle None
        if value is None:
            return "-"

        # Handle boolean
        if isinstance(value, bool):
            return "✓" if value else "✗"

        return value
    except (AttributeError, TypeError):
        return "-"


@register.filter
def field_type(field):
    """Get the type of a form field."""
    return field.field.__class__.__name__


@register.filter
def is_checkbox(field):
    """Check if field is a checkbox."""
    return field.field.widget.__class__.__name__ in [
        "CheckboxInput",
        "CheckboxSelectMultiple",
    ]


@register.filter
def is_select(field):
    """Check if field is a select."""
    return field.field.widget.__class__.__name__ in ["Select", "SelectMultiple"]


@register.filter
def is_textarea(field):
    """Check if field is a textarea."""
    return field.field.widget.__class__.__name__ == "Textarea"


@register.filter
def is_file(field):
    """Check if field is a file input."""
    return field.field.widget.__class__.__name__ in ["FileInput", "ClearableFileInput"]


@register.filter
def is_date(field):
    """Check if field is a date input."""
    try:
        # Try to get widget from field.field (Django form field structure)
        widget = field.field.widget
    except AttributeError:
        # If field doesn't have field attribute, try direct widget access
        try:
            widget = field.widget
        except AttributeError:
            return False

    return widget.__class__.__name__ == "DateInput"
