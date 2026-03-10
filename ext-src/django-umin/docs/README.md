# django-umin Documentation

This directory contains the Sphinx documentation for django-umin.

## Building the Documentation

### Prerequisites

Install Sphinx and dependencies:

```bash
cd docs
python -m venv ../docs-env
source ../docs-env/bin/activate  # On Windows: ..\docs-env\Scripts\activate
pip install sphinx myst-parser sphinx-rtd-theme
```

### Build HTML

```bash
cd docs
source ../docs-env/bin/activate
make html
```

The generated HTML will be in `build/html/`.

### View Locally

```bash
cd build/html
python -m http.server 8001
```

Then open http://localhost:8001 in your browser.

### Clean Build

```bash
make clean
make html
```

## Documentation Structure

```
docs/
├── source/
│   ├── index.md              # Main index page
│   ├── quickstart.md         # Quick start guide
│   ├── features.md           # Features documentation
│   ├── bulk-actions.md       # Bulk actions guide
│   ├── api.md                # API reference
│   ├── contributing.md       # Contributing guidelines
│   ├── conf.py               # Sphinx configuration
│   ├── _static/              # Static files (CSS, images)
│   └── _templates/           # Custom templates
├── build/                    # Generated documentation
│   └── html/                 # HTML output
├── Makefile                  # Unix make commands
└── make.bat                  # Windows batch file

```

## Writing Documentation

### Markdown Support

This project uses [MyST Parser](https://myst-parser.readthedocs.io/) for Markdown support.

Supported features:
- Standard Markdown
- Code blocks with syntax highlighting
- Admonitions (notes, warnings, etc.)
- Definition lists
- Task lists

### Code Examples

````markdown
```python
from django_umin.views import CRUDView

class BookCRUD(CRUDView):
    model = Book
```
````

### Admonitions

```markdown
:::{note}
This is a note.
:::

:::{warning}
This is a warning.
:::
```

### Cross-References

```markdown
See [Quick Start](quickstart.md) for installation.
```

### Table of Contents

```markdown
```{toctree}
:maxdepth: 2

quickstart
features
api
```
```

## Deployment

### Read the Docs

The documentation can be hosted on Read the Docs:

1. Connect your GitHub repository to Read the Docs
2. Configure the build:
   - Python version: 3.10+
   - Requirements file: Not needed (uses Sphinx autodoc)
   - Configuration file: `docs/source/conf.py`

### GitHub Pages

To deploy to GitHub Pages:

```bash
# Build docs
cd docs
make html

# Copy to gh-pages branch
git checkout gh-pages
cp -r build/html/* .
git add .
git commit -m "Update documentation"
git push origin gh-pages
```

## Theme

We use the [Read the Docs theme](https://sphinx-rtd-theme.readthedocs.io/) for a modern, mobile-friendly appearance.

## Screenshots

Documentation screenshots are available in `screenshots/`:
- `01-index-page.jpg` - Main documentation page
- `02-bulk-actions-page.jpg` - Bulk actions documentation
- `03-api-reference-page.jpg` - API reference page

## Contributing

When adding new documentation:

1. Create a new `.md` file in `source/`
2. Add it to the `toctree` in `index.md`
3. Build and verify: `make html`
4. Test all links and examples
5. Submit a PR

## License

The documentation is licensed under the same license as the project.
