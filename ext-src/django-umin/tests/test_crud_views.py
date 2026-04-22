"""Tests for CRUD view customization hooks and HTMX responses."""

import json

import pytest
from django.db import models
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from django.urls import path

from django_umin.views import CRUDDeleteView, CRUDUpdateView, CRUDView


class Book(models.Model):
    """Test model used for CRUD view unit tests."""

    title = models.CharField(max_length=255)

    class Meta:
        app_label = "tests"


urlpatterns = [
    path("books/", lambda request: HttpResponse("ok"), name="book_list"),
]


class BookCRUD(CRUDView):
    """CRUD view with overridable hooks for tests."""

    model = Book


class CustomBookCRUD(BookCRUD):
    """CRUD view with custom presentation hooks for tests."""

    htmx_enabled = False

    def get_form_title(self, action, obj=None):
        return f"{action} custom title"

    def get_breadcrumb_url(self, action, obj=None):
        return "/custom/breadcrumb/"

    def get_breadcrumb_label(self, action, obj=None):
        return "Custom books"

    def get_cancel_url(self, action, obj=None):
        return "/custom/cancel/"

    def get_submit_label(self, action, obj=None):
        return f"{action} now"


class HookTrackingCRUD(BookCRUD):
    """CRUD view that exposes queryset/object hook usage."""

    def __init__(self):
        super().__init__()
        self.update_queryset = object()
        self.delete_queryset = object()
        self.object_calls = []

    def get_update_queryset(self, request):
        return self.update_queryset

    def get_delete_queryset(self, request):
        return self.delete_queryset

    def get_object(self, request, queryset=None, **kwargs):
        self.object_calls.append((queryset, kwargs))
        return "resolved-object"


@pytest.fixture
def request_factory():
    """Provide a request factory for view unit tests."""
    return RequestFactory()


@pytest.fixture
def book():
    """Provide an unsaved model instance for response tests."""
    return Book(title="Django Umin")


@pytest.fixture
def book_crud():
    """Provide the default CRUD view."""
    return BookCRUD()


@pytest.fixture
def custom_book_crud():
    """Provide a CRUD view with custom presentation hooks."""
    return CustomBookCRUD()


@pytest.fixture
def hook_tracking_crud():
    """Provide a CRUD view that tracks queryset/object hook calls."""
    return HookTrackingCRUD()


@override_settings(ROOT_URLCONF=__name__)
def test_get_form_context_uses_custom_hook_values(custom_book_crud, request_factory, book):
    """Form context should expose the values returned by presentation hooks."""
    request = request_factory.get("/books/create/")

    context = custom_book_crud.get_form_context(request, "Update", obj=book)

    assert context["crud_view"] is custom_book_crud
    assert context["model_name"] == "book"
    assert context["action"] == "Update"
    assert context["url_namespace"] == "book"
    assert context["form_title"] == "Update custom title"
    assert context["breadcrumb_url"] == "/custom/breadcrumb/"
    assert context["breadcrumb_label"] == "Custom books"
    assert context["cancel_url"] == "/custom/cancel/"
    assert context["submit_label"] == "Update now"
    assert context["htmx_enabled"] is False


@override_settings(ROOT_URLCONF=__name__)
def test_get_htmx_success_response_redirects_by_default(book_crud, request_factory, book):
    """HTMX success responses should redirect and emit a notification by default."""
    request = request_factory.post("/books/create/", HTTP_HX_REQUEST="true")

    response = book_crud.get_htmx_success_response(
        request=request,
        obj=book,
        form=None,
        message="Created successfully",
        action="Create",
    )

    assert response.status_code == 200
    assert response.content == b""
    assert response["HX-Redirect"] == "/books/"
    assert json.loads(response["HX-Trigger"]) == {
        "labzero:notify": {
            "type": "success",
            "message": "Created successfully",
        }
    }


@override_settings(ROOT_URLCONF=__name__)
def test_get_htmx_success_response_renders_form_when_redirect_disabled(
    monkeypatch, request_factory, book
):
    """HTMX responses can re-render the form instead of redirecting."""
    crud_view = BookCRUD()
    crud_view.htmx_redirect_on_success = False
    request = request_factory.post("/books/1/", HTTP_HX_REQUEST="true")

    captured = {}

    def fake_render_to_string(template_name, context, request_arg):
        captured["template_name"] = template_name
        captured["context"] = context
        captured["request"] = request_arg
        return "<div>rendered form</div>"

    monkeypatch.setattr("django_umin.views.render_to_string", fake_render_to_string)

    response = crud_view.get_htmx_success_response(
        request=request,
        obj=book,
        form=None,
        message="Updated successfully",
        action="Update",
    )

    assert response.status_code == 200
    assert response.content == b"<div>rendered form</div>"
    assert "HX-Redirect" not in response
    assert captured["template_name"] == "django_umin/form_htmx.html"
    assert captured["context"]["object"] is book
    assert captured["context"]["form"].instance is book
    assert captured["request"] is request
    assert json.loads(response["HX-Trigger"]) == {
        "labzero:notify": {
            "type": "success",
            "message": "Updated successfully",
        }
    }


def test_update_view_uses_custom_queryset_and_object_hooks(
    hook_tracking_crud, request_factory
):
    """Update views should delegate queryset and object lookup to the CRUD view."""
    view = CRUDUpdateView(crud_view=hook_tracking_crud)
    view.request = request_factory.get("/books/1/")
    view.kwargs = {"pk": 1}

    queryset = view.get_queryset()
    obj = view.get_object()

    assert queryset is hook_tracking_crud.update_queryset
    assert obj == "resolved-object"
    assert hook_tracking_crud.object_calls == [
        (hook_tracking_crud.update_queryset, {"pk": 1})
    ]


def test_delete_view_uses_custom_queryset_and_object_hooks(
    hook_tracking_crud, request_factory
):
    """Delete views should delegate queryset and object lookup to the CRUD view."""
    view = CRUDDeleteView(crud_view=hook_tracking_crud)
    view.request = request_factory.get("/books/1/delete/")
    view.kwargs = {"pk": 1}

    queryset = view.get_queryset()
    obj = view.get_object()

    assert queryset is hook_tracking_crud.delete_queryset
    assert obj == "resolved-object"
    assert hook_tracking_crud.object_calls == [
        (hook_tracking_crud.delete_queryset, {"pk": 1})
    ]
