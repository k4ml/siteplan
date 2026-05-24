import pytest
from django.test import RequestFactory
from django.template import Context, Template

from siteplan.models import AnalyticsSetting


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.mark.django_db
class TestAnalyticsCodeTag:
    """Tests for the {% analytics_code %} template tag."""

    def test_renders_code_in_head_when_placement_is_head(self, rf):
        setting = AnalyticsSetting.objects.create(
            analytics_code="<script>console.log('ga')</script>",
            placement="head",
            excluded_paths="",
            site_id=1,
        )
        request = rf.get("/")
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert "<script>" in rendered

    def test_does_not_render_in_head_when_placement_is_body(self, rf):
        AnalyticsSetting.objects.create(
            analytics_code="<script>console.log('ga')</script>",
            placement="body",
            excluded_paths="",
            site_id=1,
        )
        request = rf.get("/")
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert rendered == ""

    def test_renders_in_body_when_placement_is_body(self, rf):
        AnalyticsSetting.objects.create(
            analytics_code="<script>console.log('ga')</script>",
            placement="body",
            excluded_paths="",
            site_id=1,
        )
        request = rf.get("/")
        template = Template(
            '{% load analytics %}{% analytics_code "body" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert "<script>" in rendered

    def test_excludes_matching_path(self, rf):
        AnalyticsSetting.objects.create(
            analytics_code="<script>console.log('ga')</script>",
            placement="head",
            excluded_paths="/admin\n/cms",
            site_id=1,
        )
        request = rf.get("/admin/settings/")
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert rendered == ""

    def test_excluded_path_does_not_match_unrelated_path(self, rf):
        AnalyticsSetting.objects.create(
            analytics_code="<script>console.log('ga')</script>",
            placement="head",
            excluded_paths="/admin\n/cms",
            site_id=1,
        )
        request = rf.get("/app/dashboard/")
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert "<script>" in rendered

    def test_excluded_path_prefix_match(self, rf):
        """A prefix like '/admin' should also exclude '/admin/foo'."""
        AnalyticsSetting.objects.create(
            analytics_code="<script>console.log('ga')</script>",
            placement="head",
            excluded_paths="/admin",
            site_id=1,
        )
        request = rf.get("/admin/foo/bar")
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert rendered == ""

    def test_empty_code_returns_empty_string(self, rf):
        AnalyticsSetting.objects.create(
            analytics_code="",
            placement="head",
            excluded_paths="",
            site_id=1,
        )
        request = rf.get("/")
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert rendered == ""

    def test_no_request_returns_empty_string(self):
        """When there's no request in context, return empty string safely."""
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({}))
        assert rendered == ""

    def test_no_setting_returns_empty_string(self, rf):
        """When no AnalyticsSetting exists, return empty string."""
        request = rf.get("/")
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert rendered == ""

    def test_blank_lines_in_excluded_paths_ignored(self, rf):
        AnalyticsSetting.objects.create(
            analytics_code="<script>console.log('ga')</script>",
            placement="head",
            excluded_paths="/admin\n\n/cms\n\n",
            site_id=1,
        )
        request = rf.get("/admin/")
        template = Template(
            '{% load analytics %}{% analytics_code "head" %}'
        )
        rendered = template.render(Context({"request": request}))
        assert rendered == ""
