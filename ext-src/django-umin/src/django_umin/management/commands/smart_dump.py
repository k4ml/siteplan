"""
Management command: smart_dump

Intelligently inspects a Django model and its related objects,
printing a rich, human-readable tree to the console.

Usage:
    python manage.py smart_dump <AppLabel.ModelName> [filters] [options]

Examples:
    python manage.py smart_dump shop.Order
    python manage.py smart_dump shop.Order status=pending
    python manage.py smart_dump shop.Order id=42
    python manage.py smart_dump shop.Order user__email=foo@bar.com --depth 3
    python manage.py smart_dump shop.Order --limit 5 --depth 1 --no-reverse

Background

Most of the time debugging django app involved inspecting models data to see
it being saved correctly or not like doing print(SomeModel.objects.filter(some__filter="xxxx")).
This is very tedious especially when it involved related objects.
I'm thinking of having management command smart_dump(SomeModel) that
intelligently inspect the models and related object.
"""

import textwrap
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import models


# ── ANSI colours (gracefully degrade on Windows/pipes) ────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
RED = "\033[31m"
BLUE = "\033[34m"


def c(text, *codes):
    return "".join(codes) + str(text) + RESET


# ── Helpers ───────────────────────────────────────────────────────────────────

MAX_STR_LEN = 120  # truncate long field values in display


def _fmt_value(value):
    if value is None:
        return c("None", DIM)
    if isinstance(value, bool):
        return c(value, GREEN if value else RED)
    s = str(value)
    if len(s) > MAX_STR_LEN:
        s = s[:MAX_STR_LEN] + c(" …[truncated]", DIM)
    return s


def _model_label(model):
    return f"{model._meta.app_label}.{model.__name__}"


def _get_forward_relations(model):
    """FK and OneToOne fields on this model pointing outward."""
    result = []
    for field in model._meta.get_fields():
        if isinstance(field, (models.ForeignKey, models.OneToOneField)):
            result.append(field)
    return result


def _get_reverse_relations(model):
    """Reverse FK / reverse OneToOne / ManyToMany (both directions)."""
    result = []
    for rel in model._meta.get_fields():
        # Reverse FK / OneToOne
        if isinstance(rel, (models.fields.related.ForeignObjectRel,)):
            if not isinstance(rel, models.ManyToManyRel):  # handled below
                result.append(rel)
        # ManyToMany (declared here OR on the other side)
        elif isinstance(rel, models.ManyToManyField):
            result.append(rel)
        elif isinstance(rel, models.ManyToManyRel):
            result.append(rel)
    return result


def _concrete_fields(instance):
    """All concrete (non-relation) fields on an instance."""
    return [
        f
        for f in instance._meta.get_fields()
        if isinstance(f, models.Field) and not f.is_relation and not f.many_to_many
    ]


# ── Core renderer ─────────────────────────────────────────────────────────────


class SmartDumper:
    def __init__(
        self,
        max_depth=2,
        show_reverse=True,
        show_m2m=True,
        indent_size=4,
        limit=50,
        no_color=False,
        struct_only=False,
    ):
        self.max_depth = max_depth
        self.show_reverse = show_reverse
        self.show_m2m = show_m2m
        self.indent = " " * indent_size
        self.limit = limit
        self.no_color = no_color
        self.struct_only = struct_only
        self._seen = set()  # (model_label, pk) – loop guard

    def _c(self, text, *codes):
        return text if self.no_color else c(text, *codes)

    def dump(self, queryset, prefix=""):
        count = queryset.count()
        model = queryset.model
        label = _model_label(model)
        print(
            prefix
            + self._c(f"[{label}]", BOLD, CYAN)
            + f"  {self._c(count, YELLOW)} record(s)"
        )
        if count == 0:
            return
        if count > self.limit:
            print(
                prefix
                + self.indent
                + self._c(
                    f"⚠  Showing first {self.limit} of {count}. Use --limit to change.",
                    DIM,
                )
            )
        for obj in queryset[: self.limit]:
            self._dump_instance(obj, depth=0, prefix=prefix + self.indent)

    def _dump_instance(self, obj, depth, prefix):
        model = type(obj)
        label = _model_label(model)
        sig = (label, obj.pk)

        # ── loop guard (check before any output) ─────────────────────────────
        if sig in self._seen:
            print(
                prefix
                + self._c(f"┌─ {model.__name__} ", BOLD, GREEN)
                + self._c(f"(pk={obj.pk})", DIM)
                + self._c(" ↩ already shown above", DIM)
            )
            return
        self._seen.add(sig)

        print(
            prefix
            + self._c(f"┌─ {model.__name__} ", BOLD, GREEN)
            + self._c(f"(pk={obj.pk})", DIM)
        )

        # ── concrete fields ──────────────────────────────────────────────────
        if not self.struct_only:
            fields = _concrete_fields(obj)
            for i, field in enumerate(fields):
                is_last = i == len(fields) - 1
                connector = "└─" if (is_last and depth >= self.max_depth) else "├─"
                raw = getattr(obj, field.attname, None)
                display = _fmt_value(raw)
                print(
                    prefix
                    + f"│  {connector} "
                    + self._c(field.name, YELLOW)
                    + " = "
                    + display
                )

        # ── relations ────────────────────────────────────────────────────────
        if depth >= self.max_depth:
            print(prefix + self._c(f"│  └─ (max depth {self.max_depth} reached)", DIM))
            print(prefix + self._c("└─────────────────────────────────", DIM))
            return

        child_prefix = prefix + "│  "
        new_prefix = child_prefix + self.indent

        # Forward FK / O2O
        for field in _get_forward_relations(model):
            try:
                related_obj = getattr(obj, field.name)
            except Exception:
                related_obj = None
            rel_label = f"→ {field.name}"
            if related_obj is None:
                print(
                    child_prefix
                    + self._c(rel_label, MAGENTA)
                    + " = "
                    + self._c("None", DIM)
                )
            else:
                print(child_prefix + self._c(rel_label, MAGENTA))
                self._dump_instance(related_obj, depth + 1, new_prefix)

        if self.show_reverse or self.show_m2m:
            meta_fields = obj._meta.get_fields()
            for rel in meta_fields:
                # Reverse FK
                if self.show_reverse and isinstance(
                    rel, models.fields.related.ManyToOneRel
                ):
                    accessor = rel.get_accessor_name()
                    try:
                        qs = getattr(obj, accessor).all()
                    except Exception:
                        continue
                    print(
                        child_prefix
                        + self._c(f"← {accessor} (reverse FK)", BLUE)
                        + f"  {self._c(qs.count(), YELLOW)} record(s)"
                    )
                    for child in qs[: self.limit]:
                        self._dump_instance(child, depth + 1, new_prefix)

                # Reverse O2O
                elif self.show_reverse and isinstance(
                    rel, models.fields.related.OneToOneRel
                ):
                    accessor = rel.get_accessor_name()
                    try:
                        child = getattr(obj, accessor)
                    except Exception:
                        child = None
                    print(child_prefix + self._c(f"← {accessor} (reverse O2O)", BLUE))
                    if child:
                        self._dump_instance(child, depth + 1, new_prefix)
                    else:
                        print(new_prefix + self._c("None", DIM))

                # M2M
                elif self.show_m2m and isinstance(
                    rel, (models.ManyToManyField, models.ManyToManyRel)
                ):
                    try:
                        accessor = (
                            rel.name
                            if hasattr(rel, "name")
                            else rel.get_accessor_name()
                        )
                        qs = getattr(obj, accessor).all()
                    except Exception:
                        continue
                    print(
                        child_prefix
                        + self._c(f"↔ {accessor} (M2M)", MAGENTA)
                        + f"  {self._c(qs.count(), YELLOW)} record(s)"
                    )
                    for child in qs[: self.limit]:
                        self._dump_instance(child, depth + 1, new_prefix)

        print(prefix + self._c("└─────────────────────────────────", DIM))


# ── Management command ────────────────────────────────────────────────────────


class Command(BaseCommand):
    help = textwrap.dedent("""\
        Intelligently dump a model's data including related objects.

        Usage:
          python manage.py smart_dump shop.Order
          python manage.py smart_dump shop.Order status=pending
          python manage.py smart_dump shop.Order user__email=foo@bar.com --depth 3
    """)

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            help="App label and model name, e.g. shop.Order",
        )
        parser.add_argument(
            "filters",
            nargs="*",
            help="ORM filter expressions as key=value pairs, e.g. status=pending id=42",
        )
        parser.add_argument(
            "--depth",
            "-d",
            type=int,
            default=2,
            help="Max depth to follow relations (default: 2)",
        )
        parser.add_argument(
            "--limit",
            "-l",
            type=int,
            default=50,
            help="Max records per queryset (default: 50)",
        )
        parser.add_argument(
            "--no-reverse",
            action="store_true",
            default=False,
            help="Skip reverse FK / O2O relations",
        )
        parser.add_argument(
            "--no-m2m",
            action="store_true",
            default=False,
            help="Skip ManyToMany relations",
        )
        parser.add_argument(
            "--struct-only",
            action="store_true",
            default=False,
            help="Show only the relation structure (model names and relation types) without any field values",
        )

    def handle(self, *args, **options):
        raw_model = options["model"]

        # ── resolve model ──────────────────────────────────────────────────
        try:
            app_label, model_name = raw_model.split(".")
        except ValueError:
            raise CommandError(
                f"Model must be in 'app_label.ModelName' format, got: {raw_model!r}"
            )

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            raise CommandError(
                f"Cannot find model '{raw_model}'. "
                f"Make sure the app is in INSTALLED_APPS and the model name is correct."
            )

        # ── parse filters ──────────────────────────────────────────────────
        filter_kwargs = {}
        for expr in options["filters"]:
            if "=" not in expr:
                raise CommandError(
                    f"Filter expression must be key=value, got: {expr!r}"
                )
            key, _, value = expr.partition("=")
            # attempt int coercion for pk-style filters
            try:
                value = int(value)
            except ValueError:
                # boolean coercion
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
            filter_kwargs[key] = value

        # ── build queryset ─────────────────────────────────────────────────
        try:
            qs = (
                model.objects.filter(**filter_kwargs)
                if filter_kwargs
                else model.objects.all()
            )
        except Exception as e:
            raise CommandError(f"Error building queryset: {e}")

        # ── dump ───────────────────────────────────────────────────────────
        dumper = SmartDumper(
            max_depth=options["depth"],
            show_reverse=not options["no_reverse"],
            show_m2m=not options["no_m2m"],
            no_color=options["no_color"],
            limit=options["limit"],
            struct_only=options["struct_only"],
        )

        print()
        if filter_kwargs:
            print(
                c(f"  Filters: {filter_kwargs}", DIM)
                if not options["no_color"]
                else f"  Filters: {filter_kwargs}"
            )
        dumper.dump(qs)
        print()
