This is very opinionate Django project structure that we use at lalokalabs. It includes:-

- `src/` based layout to separate python code from non-python files at the project root, only
   `./src/` will be added to `PYTHONPATH` resulting in cleaner import, no accidentally any `.py`
  files suddenly available in the python namespace.
- Use `uv` to manage dependencies.
- Frontend assets integration with Vite (from `ext-src/django-umin`).
- Use pytest for testing - prefer function based tests with fixtures instead of class.
- Mailpit - Local mail testing server
- Overmind - Process manager (runs multiple services)
- Docker Compose - Dependent services (Postgres, Redis, Adminer)

## Quickstart

```
git submodule update --init --recursive
cp .env.example .env
make up
```

Add to `.env` to automatically start vite dev server:-

```
DJANGO_UMIN_VITE_DEV_MODE=True
DJANGO_UMIN_VITE_HMR_PORT=5173
```
Or run `uv run manage.py vite_build` to build it manually, such as for production deploy.

In separate terminal, run:-

```
make dev
make run
```

**IMPORTANT**
Run `./rename.sh siteplan yourappname` before running your first `make dev` as that will run initial django migrations and `AUTH_USER_MODEL` is set by default to `siteplan_user.User`. You should change it to your own custom user models.

Login to the dashboard at `/dashboard/` and using email `admin@siteplan.co` and password `picard data`.

## Notes on Github Codespaces
Vite dev server run on different port than the django dev server and unless you set it to public, it need to be authenticated first. You will need to open the css or js file directly first so that github will authenticate it. After that it should work as expected.

## Screenshots

### Dashboard
<img width="2463" height="1512" alt="Screenshot from 2025-12-06 11-16-22" src="https://github.com/user-attachments/assets/d3c67461-48df-4168-994c-a8f60ac6d0c7" />

### Login
<img width="2463" height="1512" alt="Screenshot from 2025-12-06 11-16-59" src="https://github.com/user-attachments/assets/2110614c-0064-4d7e-81e7-669e7fb72edd" />

## Customize
The default project name is `siteplan` and is used throughout the codebase for db name, settings and file/directory name. Run the script `rename.sh` to change this to your preferred project name.
