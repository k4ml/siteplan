# Contributing

We love contributions! Here's how you can help make django-umin better.

## Getting Started

### 1. Fork and Clone

```bash
git fork https://github.com/k4ml/django-umin.git
git clone https://github.com/YOUR-USERNAME/django-umin.git
cd django-umin
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-django black ruff
```

### 3. Create a Branch

```bash
git checkout -b feature/my-awesome-feature
```

## Development Workflow

### Running Tests

```bash
pytest
```

### Code Formatting

We use `black` for code formatting:

```bash
black src/django_umin/
```

### Linting

We use `ruff` for linting:

```bash
ruff check src/django_umin/
```

### Type Checking

```bash
mypy src/django_umin/
```

## Making Changes

### 1. Write Your Code

Follow these guidelines:
- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Write tests for new features
- Update documentation

### 2. Test Your Changes

```bash
# Run tests
pytest

# Check coverage
pytest --cov=django_umin
```

### 3. Update Documentation

If you're adding features or changing behavior:
- Update relevant `.md` files in `docs/source/`
- Add examples to docstrings
- Update the changelog

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git commit -m "feat: Add support for custom action permissions

- Add permission_required attribute to Action class
- Update documentation with permission examples
- Add tests for permission checking"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build/tooling changes

## Submitting Changes

### 1. Push to Your Fork

```bash
git push origin feature/my-awesome-feature
```

### 2. Create Pull Request

Go to GitHub and create a pull request:

1. Navigate to your fork
2. Click "New pull request"
3. Select your feature branch
4. Fill in the PR template:
   - Clear title
   - Description of changes
   - Screenshots (if UI changes)
   - Breaking changes (if any)

### 3. Code Review

- Respond to feedback
- Make requested changes
- Push updates to your branch (PR updates automatically)

## Development Guidelines

### Code Style

- Use 4 spaces for indentation
- Maximum line length: 88 characters (black default)
- Use type hints where appropriate
- Follow Django coding style

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Test on multiple Django versions
- Test both HTMX and non-HTMX scenarios

### Documentation

- Add docstrings to all public APIs
- Update user documentation for new features
- Include code examples
- Add screenshots for UI changes

### Commit Messages

Good commit message:
```
feat: Add bulk action permissions

- Add has_action_permission method to CRUDView
- Check permissions before showing actions
- Add tests for permission checks
- Update documentation

Closes #42
```

## Types of Contributions

### Bug Reports

Found a bug? Open an issue:

1. Clear title describing the bug
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Django/Python versions
6. Any error messages

### Feature Requests

Have an idea? Open an issue:

1. Clear description of the feature
2. Use cases
3. Example code (if applicable)
4. Why it's useful

### Documentation

- Fix typos
- Improve examples
- Add missing documentation
- Translate documentation

### Code

- Fix bugs
- Add features
- Improve performance
- Refactor code

## Getting Help

- 💬 Open a [GitHub Discussion](https://github.com/k4ml/django-umin/discussions)
- 🐛 Report bugs in [Issues](https://github.com/k4ml/django-umin/issues)
- 📧 Email: kamal@koditi.my

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Documentation

Thank you for contributing to django-umin! 🎉
