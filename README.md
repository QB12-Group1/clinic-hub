# Clinic Hub

**Clinic Hub** is an online reservation and booking system currently in active development. The goal of this project is to simplify and automate appointment scheduling for clinics and healthcare providers.

## Frontend foundation

The project includes a Django-native frontend foundation built with Tailwind CSS, daisyUI, HTMX, Alpine.js, and lucide icons. The example dashboard is available at `/` and uses fake clinic data so the patterns are easy to replace with real querysets.

### Local development

Install Node.js 22+ and run:

```bash
npm install
npm run dev
```

In a second terminal, start Django with `uv run python manage.py runserver`. The CSS and JavaScript watchers write to `static/dist/`; Django serves these during development and nginx serves collected assets in production.

For a production build, run `npm run build` before `uv run python manage.py collectstatic --noinput`. The Dockerfile performs this build automatically, then the existing entrypoint runs migrations and collectstatic.

### Reusing the base

Extend `templates/base.html` for new pages, load assets with `{% templatetag openblock %} static 'dist/app.css' {% templatetag closeblock %}` / `{% templatetag openblock %} static 'dist/app.js' {% templatetag closeblock %}`, and use `surface`, `eyebrow`, and daisyUI component classes as shared primitives. Use Alpine for local UI state, HTMX for server-rendered partial updates, and `data-lucide="icon-name"` for icons.

## Current Project Status
This project is under active development. Features are being built out, and there is no stable installation process at this time.

## Contributing
Since the project is in its early stages, we would love your help! If you are looking to contribute, please check out the [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to get involved and start helping us build.
