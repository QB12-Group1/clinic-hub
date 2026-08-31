# Contributing to clinic-hub

Thanks for contributing to clinic-hub. This guide covers the local development
setup and the checks expected before opening a pull request.

## Prerequisites

- Python 3.12 or newer
- Git
- [uv](https://docs.astral.sh/uv/) for dependency and virtual-environment management
- PostgreSQL

Check your installed versions:

```bash
python --version
uv --version
psql --version
```

Install uv if needed:

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Set up the project

Clone the repository, then install the locked runtime and development
dependencies:

```bash
git clone <repository-url>
cd clinic-hub
uv sync --locked --group dev
```

### PostgreSQL

PostgreSQL is the project's development and production database. The Django
database settings are still being configured; the current SQLite configuration
is temporary and should not be considered the supported project setup.

Create a local PostgreSQL role and database for clinic-hub:

```sql
CREATE USER clinic_hub WITH PASSWORD 'choose-a-local-password';
CREATE DATABASE clinic_hub OWNER clinic_hub;
```

Keep local database credentials in an ignored `.env` file—never commit them.
Once the PostgreSQL settings are added, use the environment-variable names
documented in the repository's example environment file. If that file is not
present yet, check the active database-configuration work for the expected
names and values.

> **Configuration status:** `core/settings.py` currently points Django at a
> temporary SQLite database. Until the PostgreSQL configuration is merged,
> `migrate`, `test`, and `runserver` will use SQLite rather than PostgreSQL.

Apply migrations and start the development server:

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. Do not use the development settings
or their built-in secret key in production.

## Development workflow

Create a focused branch from the latest `dev` branch:

```bash
git switch dev
git pull --ff-only origin dev
git switch -c <short-description>
```

Keep changes focused and include or update Django tests for behavior you change.
When models change, create and apply migrations:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

Run the test suite with:

```bash
uv run python manage.py test
```

## Quality checks

Code-quality checks are managed through pre-commit. The configured hooks run:

- Ruff linting with automatic fixes
- Ruff formatting
- Pyright static type checking
- YAML and TOML validation
- Trailing-whitespace and end-of-file fixes
- Merge-conflict marker and debug-statement checks

Install the hooks once per clone:

```bash
uv run pre-commit install
```

After installation, the checks run automatically whenever you commit. A hook
may modify files; review and stage those changes, then commit again.

Before pushing, run the complete hook suite against the repository:

```bash
uv run pre-commit run --all-files
```

Do not bypass the hooks with `--no-verify`. Fix reported issues before opening
a pull request. If a check needs an intentional exception, explain why in the
pull request.

## Commits and pull requests

Use clear, imperative commit messages, for example:

```text
Add appointment availability validation
```

Before opening a pull request:

- Rebase or update your branch from `dev`.
- Run the test suite and all pre-commit checks.
- Include migrations when required.
- Describe what changed, why it changed, and how it was tested.
- Add screenshots or a short recording for user-facing changes.

Open pull requests against `dev`. Changes are reviewed before merging; merged
feature branches may be deleted. The `main` branch is reserved for stable
release-ready code.

## Reporting problems

For bugs or feature ideas, search existing issues first. Include clear
reproduction steps, expected and actual behavior, and relevant logs or
screenshots. Never include credentials, secret keys, or other sensitive
personal data in an issue or pull request.
